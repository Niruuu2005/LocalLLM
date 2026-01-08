# Local LLM Django Chat 🤖

A feature-rich Django web application for chatting with locally-hosted LLMs via Ollama, featuring **multi-mode AI interactions**, user management, and pricing tiers.

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![Django](https://img.shields.io/badge/django-5.2.5-darkgreen)
![License](https://img.shields.io/badge/license-MIT-orange)

## ✨ Features

### 🎭 Multi-Mode AI Interactions
- **💬 Normal Mode**: Standard conversational AI
- **🎓 Teacher Mode**: Pedagogical, student-friendly explanations
- **🔬 Researcher Mode**: Academic, evidence-based responses
- **🏛️ Council Mode**: Multi-model debate and synthesis (queries 2-3 models simultaneously)

### 🔐 User Management
- Registration & Login system
- User-specific chat history
- Session persistence

### 💎 Pricing Tiers
- **Free**: Access to 3B and smaller models
- **Pro ($19/mo)**: Access to 7B+ models

### 💬 Chat Features
- Real-time streaming responses
- Dynamic model selection (auto-detects installed Ollama models)
- Conversation history with timestamps
- Dark-mode premium UI

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com) installed
- At least one LLM model (e.g., `ollama pull llama3.2`)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/local-llm-django.git
cd local-llm-django
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run migrations**
```bash
python manage.py migrate
```

4. **Start Ollama** (in a separate terminal)
```bash
ollama serve
```

5. **Run the application**
```bash
python manage.py runserver
```

Or use the automated script:
```powershell
.\start_app.ps1
```

6. **Access the app**
Navigate to `http://127.0.0.1:8000/`

## 🎯 Usage

1. **Register**: Create a new account (default: Free tier)
2. **Select Mode**: Choose from Normal, Teacher, Researcher, or Council
3. **Select Model**: Pick from your installed Ollama models
4. **Chat**: Start asking questions!

### Council Mode
Council Mode is the standout feature - it queries multiple models in parallel and synthesizes their responses:
- Requires 2+ models installed
- 3-5x slower than normal mode
- Shows individual model responses before synthesis

## 📁 Project Structure

```
LocalLLM/
├── chat/                   # Main chat app
│   ├── models.py          # Database models (UserProfile, Conversation, Message)
│   ├── views.py           # Backend logic with mode-specific prompts
│   ├── templates/         # HTML templates
│   └── static/            # CSS/JS
├── local_llm/             # Django project settings
├── manage.py
├── requirements.txt
├── start_app.ps1          # Automated startup script
└── README.md
```

## 🛠️ Technologies

- **Backend**: Django 5.2.5, Python 3.13
- **AI**: Ollama Python SDK
- **Frontend**: Vanilla JavaScript, CSS (Dark Mode)
- **Database**: SQLite (easily swappable)
- **Auth**: Django built-in authentication

## 🔧 Configuration

Environment variables (`.env`):
```env
DEBUG=True
SECRET_KEY=your-secret-key
OLLAMA_API_URL=http://127.0.0.1:11434
```

## 🐳 Docker Deployment

```bash
docker-compose up
```

The `docker-compose.yml` includes both Django and Ollama services with GPU support.

## 📝 Mode Details

### Teacher Mode 🎓
System Prompt: *"You are a patient and experienced teacher..."*
- Simplifies complex concepts
- Uses analogies and examples
- Step-by-step explanations

### Researcher Mode 🔬
System Prompt: *"You are an academic researcher..."*
- Evidence-based responses
- Multiple perspectives
- Research paper structure

### Council Mode 🏛️
- Queries top 3 installed models
- Streams each model's response
- Synthesizes final answer
- Gracefully handles incompatible models

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- [Ollama](https://ollama.com) for local LLM hosting
- Django community
- All contributors

## 📧 Contact

For questions or suggestions, please open an issue on GitHub.

---

**Built with ❤️ for the local AI community**
