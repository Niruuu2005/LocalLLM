import ollama
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse, JsonResponse
from .models import Conversation, Message
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('chat')
    else:
        form = UserCreationForm()
    return render(request, 'chat/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('chat')
    else:
        form = AuthenticationForm()
    return render(request, 'chat/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def pricing_view(request):
    return render(request, 'chat/pricing.html')

@login_required
def chat_view(request):
    user_profile = request.user.userprofile
    if request.method == 'POST':
        # Dynamic default: pick first available if specific model not requested, or fallback to llama2
        default_model = 'llama2:latest'
        try:
             models_info = ollama.list()
             # ollama.list() returns ListResponse with .models attribute
             # Each model has .model attribute with the name
             installed_models = [m.model for m in models_info.models] if hasattr(models_info, 'models') else []
             if installed_models:
                 default_model = installed_models[0]
        except:
            installed_models = []
            pass

        model = request.POST.get('model')
        
        # Fallback if model not specified OR not installed
        if not model or (installed_models and model not in installed_models):
            model = default_model

        prompt = request.POST.get('prompt')
        
        if not prompt:
            return JsonResponse({'error': 'No prompt provided'}, status=400)

        # Pricing Enforcements (Simplified)
        # For local deployments, Free users can use any 3B or smaller model
        # Pro users get access to 7B+ models
        if user_profile.plan == 'free':
            # Check if model name contains indicators of large models
            restricted_patterns = ['7b', '13b', '70b', '34b']
            model_lower = model.lower()
            
            # Block only if it's clearly a large model
            if any(pattern in model_lower for pattern in restricted_patterns):
                return JsonResponse({
                    'error': f'Model "{model}" requires Pro plan. Free users can use 3B models and smaller.'
                }, status=403)

        user = request.user


        conversation_id = request.POST.get('conversation_id')
        mode = request.POST.get('mode', 'normal')  # Get mode from request

        if conversation_id:
            conv = Conversation.objects.get(id=conversation_id)
        else:
            conv = Conversation.objects.create(user=user, title=prompt[:30], mode=mode)

        # Save User Message
        Message.objects.create(conversation=conv, content=prompt, is_user=True)

        # Mode-specific system prompts
        system_prompts = {
            'teacher': "You are a patient and experienced teacher. Explain concepts clearly and simply, as if teaching a student. Use examples, analogies, and break down complex ideas into digestible steps. Encourage learning and curiosity.",
            'researcher': "You are an academic researcher. Provide detailed, evidence-based responses with proper analysis. Consider multiple perspectives, cite reasoning, and structure your responses like a research paper with clear hypotheses and conclusions.",
            'council': "You are participating in a council of AI models. Your goal is to provide a thoughtful, balanced perspective that considers multiple viewpoints before reaching a conclusion.",
            'normal': None
        }
        
        system_prompt = system_prompts.get(conv.mode)
        
        # Build messages for ollama
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': prompt})

        def stream_generator():
            full_response = ""
            try:
                # Council Mode: Multi-model debate
                if conv.mode == 'council':
                    # Get available models
                    try:
                        models_list = ollama.list()
                        available = [m.model for m in models_list.models] if hasattr(models_list, 'models') else [model]
                        # Use up to 3 models for council
                        council_models = available[:min(3, len(available))]
                    except:
                        council_models = [model]
                    
                    if len(council_models) > 1:
                        yield f"[Council Mode: Consulting {len(council_models)} models...]\n\n"
                        
                        responses = []
                        for i, m in enumerate(council_models, 1):
                            yield f"Model {i} ({m}): "
                            model_response = ""
                            stream = ollama.chat(model=m, messages=messages, stream=True)
                            for chunk in stream:
                                content = chunk['message']['content']
                                model_response += content
                                yield content
                            responses.append(f"Model {i} ({m}): {model_response}")
                            yield "\n\n"
                        
                        # Synthesize
                        yield "[Synthesizing council responses...]\n\n"
                        synthesis_prompt = f"Based on these responses from different models:\n\n{chr(10).join(responses)}\n\nProvide a final synthesized answer that combines the best insights:"
                        
                        stream = ollama.chat(model=model, messages=[{'role': 'user', 'content': synthesis_prompt}], stream=True)
                        for chunk in stream:
                            content = chunk['message']['content']
                            full_response += content
                            yield content
                    else:
                        # Fallback to single model
                        stream = ollama.chat(model=model, messages=messages, stream=True)
                        for chunk in stream:
                            content = chunk['message']['content']
                            full_response += content
                            yield content
                else:
                    # Normal, Teacher, or Researcher mode
                    stream = ollama.chat(model=model, messages=messages, stream=True)
                    for chunk in stream:
                        content = chunk['message']['content']
                        full_response += content
                        yield content
                
                # Save AI Message after stream completes
                # Note: This runs in the generator, so db connection must be thread-safe or alive.
                # Django 3.0+ handles this reasonably well in sync views with iterators, 
                # but explicit saving here is okay for simple use cases.
                Message.objects.create(conversation=conv, content=full_response, is_user=False)
            except Exception as e:
                # Handle connection errors specifically
                if "No connection could be made" in str(e) or "10061" in str(e):
                    yield "Error: Could not connect to Ollama. Is 'ollama serve' running?"
                else:
                    yield f"Error: {str(e)}"

        response = StreamingHttpResponse(stream_generator(), content_type='text/plain')
        response['X-Conversation-ID'] = conv.id
        return response

    # Get conversations for the current user only
    conversations = Conversation.objects.filter(user=request.user).order_by('-created_at')
    active_conversation = None
    conversation_id = request.GET.get('conversation_id')
    if conversation_id:
        try:
            active_conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            pass
            
    
    # Fetch available models
    try:
        models_response = ollama.list()
        # ollama.list() returns a ListResponse object with .models attribute
        # Each model object has .model attribute for the name
        available_models = [m.model for m in models_response.models] if hasattr(models_response, 'models') else []
    except Exception as e:
        print(f"Error fetching models: {e}")  # Debug
        available_models = []  # Fallback or empty if connection fails
        
    return render(request, 'chat/index.html', {
        'conversations': conversations,
        'active_conversation': active_conversation,
        'available_models': available_models
    })
