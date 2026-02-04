<p align="center">
  <img src="IDW.png" alt="Inclusive Design Wizard Logo" width="200"/>
</p>

<h1 align="center">Inclusive Design Wizard</h1>

<p align="center">
  <strong>An AI-powered accessibility consultation tool that teaches educators how to create universally designed, inclusive learning experiences.</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#using-ai-models">AI Models</a> •
  <a href="#how-it-works">How It Works</a> •
  <a href="#privacy">Privacy</a> •
  <a href="#contributing">Contributing</a>
</p>

---

## 🎯 What is Inclusive Design Wizard?

The Inclusive Design Wizard (IDW) is a desktop application that guides educators through creating accessible learning materials using:

- **Universal Design for Learning (UDL)** - A framework for designing flexible learning experiences
- **Web Content Accessibility Guidelines (WCAG)** - International standards for digital accessibility
- **Disability Justice Principles** - Centering the voices and experiences of disabled people

**The goal is to TEACH** - not just provide recommendations, but help educators understand *why* accessibility matters and *how* to implement it effectively.

---

## ✨ Features

### 🧙‍♂️ Guided Consultation Process
The AI walks you through a structured conversation covering:
- Understanding your learning context
- Analyzing learner variability
- Engagement strategies (UDL Principle 1)
- Representation options (UDL Principle 2)
- Expression alternatives (UDL Principle 3)
- WCAG compliance review
- Assessment and continuous improvement

### 🔍 AI Reasoning Transparency
**See "under the hood"** of every AI recommendation:
- **Source Materials** - Which UDL guidelines, WCAG criteria, and research inform each response
- **Confidence Levels** - How certain the AI is about recommendations and why
- **Connection to Your Task** - How advice relates to your specific context
- **Guiding Principles** - The disability justice principles driving recommendations

### 📝 Session Notes
Track your progress and insights over time:
- Add timestamped notes to any consultation
- Review previous notes when returning to a project
- Build a knowledge base of accessibility learnings

### 💾 Local Data Storage
**Your data stays on your computer:**
- All conversations saved locally in SQLite database
- No cloud sync required
- Full control over your consultation history
- Export to Word documents for sharing

### 🎓 Built-in Tutorials
Interactive tutorials on every page explain:
- How to use each feature
- What each section means
- Tips for getting the best results

### 📊 Progress Tracking
Visual indicators show:
- Current consultation phase
- Completion percentage
- Which topics have been covered

---

## 💻 Installation

### Prerequisites

- **Python 3.11 or higher** (3.14 recommended)
- **pip** (Python package manager)
- **Git** (for cloning the repository)

---

### 🍎 macOS Installation

#### Step 1: Install Python

**Option A: Using Homebrew (Recommended)**
```bash
# Install Homebrew if you don't have it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.14
```

**Option B: Download from Python.org**
1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Download the macOS installer
3. Run the installer and follow the prompts

#### Step 2: Clone the Repository
```bash
git clone https://github.com/Tech-Inclusion-Pro/Local-Inclusive-Design-Wizard.git
cd Local-Inclusive-Design-Wizard
```

#### Step 3: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 5: Run the Application
```bash
python main.py
```

---

### 🪟 Windows Installation

#### Step 1: Install Python

1. Go to [python.org/downloads/windows](https://www.python.org/downloads/windows/)
2. Download the Windows installer (64-bit recommended)
3. **Important:** Check "Add Python to PATH" during installation
4. Click "Install Now"

#### Step 2: Open Command Prompt
Press `Win + R`, type `cmd`, and press Enter

#### Step 3: Clone the Repository
```cmd
git clone https://github.com/Tech-Inclusion-Pro/Local-Inclusive-Design-Wizard.git
cd Local-Inclusive-Design-Wizard
```

#### Step 4: Create Virtual Environment
```cmd
python -m venv venv
venv\Scripts\activate
```

#### Step 5: Install Dependencies
```cmd
pip install -r requirements.txt
```

#### Step 6: Run the Application
```cmd
python main.py
```

---

### 🐧 Linux Installation

#### Step 1: Install Python and Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip git
```

**Fedora:**
```bash
sudo dnf install python3.11 python3-pip git
```

**Arch Linux:**
```bash
sudo pacman -S python python-pip git
```

#### Step 2: Clone the Repository
```bash
git clone https://github.com/Tech-Inclusion-Pro/Local-Inclusive-Design-Wizard.git
cd Local-Inclusive-Design-Wizard
```

#### Step 3: Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 5: Run the Application
```bash
python main.py
```

---

## 🤖 Using AI Models

The Inclusive Design Wizard supports both **local** and **cloud** AI models, giving you flexibility in how you use the tool.

### 🏠 Local AI Models (Recommended for Privacy)

Local models run entirely on your computer. **No data is sent to external servers.**

#### Option 1: Ollama (Easiest)

1. **Install Ollama:**
   - **macOS:** `brew install ollama` or download from [ollama.ai](https://ollama.ai)
   - **Windows:** Download from [ollama.ai](https://ollama.ai)
   - **Linux:** `curl -fsSL https://ollama.ai/install.sh | sh`

2. **Start Ollama:**
   ```bash
   ollama serve
   ```

3. **Download a Model:**
   ```bash
   # Recommended models (choose one):
   ollama pull gemma3:4b      # Good balance of speed and quality
   ollama pull llama3.2       # Meta's latest model
   ollama pull mistral        # Fast and efficient
   ```

4. **Configure in App:**
   - Open Settings in the app
   - Select "Local AI"
   - Choose "Ollama" as provider
   - Select your downloaded model
   - Click "Test Connection" to verify

#### Option 2: LM Studio

1. Download from [lmstudio.ai](https://lmstudio.ai)
2. Download a model within LM Studio
3. Start the local server (port 1234)
4. In the app, select "LM Studio" as your provider

#### Option 3: GPT4All

1. Download from [gpt4all.io](https://gpt4all.io)
2. Download and load a model
3. Enable the API server
4. In the app, select "GPT4All" as your provider

---

### ☁️ Cloud AI Models

Cloud models offer more powerful responses but send data to external servers.

#### OpenAI (GPT-4)

1. Get an API key from [platform.openai.com](https://platform.openai.com)
2. In Settings, select "Cloud AI" → "OpenAI"
3. Enter your API key
4. Select model (gpt-4o recommended)

#### Anthropic (Claude)

1. Get an API key from [console.anthropic.com](https://console.anthropic.com)
2. In Settings, select "Cloud AI" → "Anthropic"
3. Enter your API key
4. Select model (claude-sonnet-4 recommended)

---

### Comparison: Local vs Cloud

| Feature | Local Models | Cloud Models |
|---------|--------------|--------------|
| **Privacy** | ✅ Complete - no data leaves your computer | ⚠️ Data sent to provider servers |
| **Cost** | ✅ Free after setup | 💰 Pay per use |
| **Speed** | Depends on hardware | Generally fast |
| **Quality** | Good for most uses | Highest quality available |
| **Offline** | ✅ Works without internet | ❌ Requires internet |
| **Setup** | More initial setup | Quick API key setup |

**Recommendation:** Start with Ollama + Gemma3 or Llama3.2 for the best balance of privacy, quality, and ease of setup.

---

## 📖 How It Works

### Starting a Consultation

1. **Launch the App** and log in (or use local mode)
2. **Click "Start New Consultation"** on the dashboard
3. **Name your consultation** (e.g., "Biology 101 Lab Redesign")
4. **Select consultation type** (or use Custom)
5. **Begin the guided conversation**

### The Consultation Process

The AI guides you through phases based on UDL and WCAG frameworks:

```
📍 Context Gathering
   ↓
📍 Learner Analysis
   ↓
📍 Engagement (UDL Principle 1)
   ↓
📍 Representation (UDL Principle 2)
   ↓
📍 Expression (UDL Principle 3)
   ↓
📍 WCAG Review
   ↓
📍 Assessment & Next Steps
```

### Understanding AI Reasoning

Click the **"AI Reasoning"** button to see:

- **Framework Applied** - Which UDL guideline or WCAG principle
- **Source Materials** - Actual references (CAST guidelines, research papers)
- **Confidence Level** - How certain the AI is (High/Medium/Low)
- **Connection to Your Task** - Why this matters for your specific project
- **Guiding Principle** - The disability justice principle driving the recommendation

This transparency helps you **learn** accessibility principles, not just receive recommendations.

### Adding Notes

1. Go to the **Dashboard**
2. Find your consultation card
3. Click **"Notes"**
4. Add your insights, questions, or to-do items
5. Click **"Save Note"** - automatically timestamped

### Exporting Your Work

1. Open a consultation
2. Click **"Export"** in the header
3. Save as a Word document (.docx)
4. Share with colleagues or keep for reference

---

## 🔒 Privacy

### Where is Data Stored?

All data is stored **locally** on your computer:

| Platform | Location |
|----------|----------|
| **macOS** | `~/Library/Application Support/Inclusive Design Wizard/` |
| **Windows** | `%APPDATA%\Inclusive Design Wizard\` |
| **Linux** | `~/.inclusive-design-wizard/` |

### What's Stored?

- **inclusive_design.db** - SQLite database containing:
  - User account (if not using local mode)
  - Consultation sessions
  - Conversation history
  - Notes
  - Settings

### Privacy with Local AI Models

When using **local AI models** (Ollama, LM Studio, GPT4All):
- ✅ Conversations never leave your computer
- ✅ No data sent to cloud servers
- ✅ Works completely offline
- ✅ Full control over your data

### Privacy with Cloud AI Models

When using **cloud AI models** (OpenAI, Anthropic):
- ⚠️ Conversations are sent to the provider's servers
- ⚠️ Subject to provider's data policies
- ⚠️ Requires internet connection

**Recommendation:** Use local models for sensitive or confidential content.

---

## 🎓 Learning Objectives

The Inclusive Design Wizard is designed to teach:

### UDL Principles
- **Engagement** - How to motivate and sustain learner interest
- **Representation** - How to present information in multiple ways
- **Action & Expression** - How to let learners demonstrate knowledge flexibly

### WCAG Guidelines
- **Perceivable** - Content accessible to all senses
- **Operable** - Interfaces everyone can use
- **Understandable** - Clear, consistent content
- **Robust** - Works with assistive technologies

### Disability Justice
- **"Nothing About Us Without Us"** - Centering disabled voices
- **Presume Competence** - Barriers are in design, not people
- **Design for the Margins** - What helps marginalized learners helps everyone

---

## 📋 Requirements

Create a `requirements.txt` file with:

```
PyQt6>=6.5.0
sqlalchemy>=2.0.0
aiohttp>=3.8.0
python-docx>=0.8.11
bcrypt>=4.0.0
```

---

## 🛠️ Troubleshooting

### "Model not found" error
- Make sure Ollama is running (`ollama serve`)
- Verify the model is downloaded (`ollama list`)
- Check Settings and select the correct model

### App won't start
- Ensure Python 3.11+ is installed (`python --version`)
- Activate virtual environment (`source venv/bin/activate`)
- Install dependencies (`pip install -r requirements.txt`)

### AI responses are slow
- Local models depend on your hardware
- Try a smaller model (e.g., `gemma3:4b` instead of larger variants)
- Cloud models are generally faster

### Connection test fails
- For Ollama: Ensure `ollama serve` is running
- For cloud: Verify your API key is correct
- Check your internet connection (for cloud models)

---

## 🤝 Contributing

We welcome contributions! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Areas for Contribution
- Additional consultation templates
- More AI provider integrations
- Accessibility improvements (we practice what we teach!)
- Translations
- Documentation improvements

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🙏 Acknowledgments

- **CAST** - For the UDL Guidelines
- **W3C WAI** - For WCAG standards
- **Sins Invalid** - For Disability Justice framework
- **The disability community** - For the principle "Nothing About Us Without Us"

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/Tech-Inclusion-Pro/Local-Inclusive-Design-Wizard/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Tech-Inclusion-Pro/Local-Inclusive-Design-Wizard/discussions)

---

<p align="center">
  <strong>Built with ❤️ for inclusive education</strong>
</p>

<p align="center">
  <em>"When we design for disabled learners, we create better experiences for everyone."</em>
</p>
