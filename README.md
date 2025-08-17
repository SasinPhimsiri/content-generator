# Content Generator

## 🎯 Quick Demo
Try it instantly without any setup: **[Live Demo on Hugging Face Spaces](https://huggingface.co/spaces/Sasinp/content_generator)** 🚀

No installation required - just click and start generating professional business content!

---

## 🚀 Get Started in 3 Steps

### Step 1: Install Ollama

#### On macOS/Linux:
```bash
# On Mac:
brew install ollama

# On Linux:
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama
ollama serve

# Download the AI model (this might take a few minutes)
ollama pull qwen3:4b-instruct-2507-q4_K_M
```

#### On Windows:
```powershell
# Download and install Ollama from https://ollama.ai/download/windows
# Or use winget:
winget install Ollama.Ollama

# Start Ollama (it should start automatically after installation)
# If not, run from Command Prompt or PowerShell:
ollama serve

# Download the AI model (this might take a few minutes)
ollama pull qwen3:4b-instruct-2507-q4_K_M
```

### Step 2: Set Up the Project

#### On macOS/Linux:
```bash
# Download and enter the project
git clone https://github.com/SasinPhimsiri/content-generator.git
cd content-generator

# Install everything (takes 1-2 minutes)
./start.sh
```

#### On Windows:
```powershell
# Download and enter the project
git clone [your-repo]
cd content-generator

# Install uv (Python package manager)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Install dependencies
uv sync

# Copy environment file
copy env.example .env

# Create necessary directories
mkdir logs, data\simple_db -Force

# Update style learning and test
uv run python main.py style
uv run python main.py test

# Start the system
uv run python main.py full
```

### Step 3: Start Creating!
The system will automatically open at:
- **Web Interface**: http://localhost:7860 (for writing articles)
- **API**: http://localhost:8000 (for developers)
- **API Documentation**: http://localhost:8000/docs (interactive API docs)

That's it! You're ready to create amazing content.

## 🎨 How to Use

### 🌐 Web Interface (UI) Usage

#### Basic Content Generation:
1. **Open the web interface** at http://localhost:7860
2. **Enter your topic** (e.g., "Digital Transformation in Retail", "AI in Healthcare")
3. **Choose category** from dropdown (Technology Trends, Business Strategy, Industry Insights, etc.)
4. **Select industry** from dropdown (Technology, Healthcare, Finance, Retail, etc.)
5. **Add SEO keywords** (optional) - separate with commas
6. **Click "Generate Content"** and wait 2-3 minutes
7. **Review your article** - it appears in the output section
8. **Download or copy** - your article is automatically saved to Excel!

#### Advanced Options:
- **Target Audience**: Specify who you're writing for (default: "business executives")
- **Content Length**: Choose short (400-500 words), medium (600-800 words), or long (1000+ words)
- **Source URLs**: Add up to 5 reference websites for additional context
- **Additional Context**: Paste extra information, requirements, or specific points to cover
- **Content Style**: The system automatically learns and applies Jenosize's writing style

#### UI Features:
- **Real-time Progress**: See generation progress with agent status updates
- **Quality Scoring**: Each article gets a quality score (0-10)
- **Instant Preview**: Review content before saving
- **Excel Export**: Automatic saving to `generated_content/jenosize_content_history.xlsx`
- **History Tracking**: All generated content is saved with metadata

### 🔗 API Usage

#### Base URL: `http://localhost:8000`

#### 1. Health Check
```bash
curl -X GET "http://localhost:8000/health"
```

Response:
```json
{
  "status": "healthy",
  "timestamp": 1703123456,
  "version": "1.0.0",
  "model_available": true,
  "model_name": "qwen3:4b-instruct-2507-q4_K_M"
}
```

#### 2. Generate Content
```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "AI in Healthcare Diagnostics",
    "category": "Technology Trends",
    "industry": "Healthcare",
    "target_audience": "healthcare executives",
    "seo_keywords": ["AI", "healthcare", "diagnostics", "medical technology"],
    "content_length": "medium",
    "source_urls": ["https://example.com/ai-healthcare"],
    "additional_context": "Focus on practical implementation challenges"
  }'
```

#### 3. API Request Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `topic` | string | Yes | Main topic (3-200 characters) |
| `category` | string | No | Content category |
| `industry` | string | No | Target industry |
| `target_audience` | string | No | Target audience (default: "business executives") |
| `seo_keywords` | array | No | Up to 10 SEO keywords |
| `content_length` | string | No | "short", "medium", or "long" (default: "medium") |
| `source_urls` | array | No | Up to 5 reference URLs |
| `additional_context` | string | No | Extra context (max 1000 characters) |

#### 4. API Response Structure
```json
{
  "content": "Generated article content...",
  "metadata": {
    "topic": "AI in Healthcare Diagnostics",
    "category": "Technology Trends",
    "industry": "Healthcare",
    "target_audience": "healthcare executives",
    "seo_keywords": ["AI", "healthcare", "diagnostics"],
    "estimated_word_count": 750,
    "content_length": "medium"
  },
  "quality_score": 9.2,
  "workflow_data": {
    "research_insights": "Key insights from research phase...",
    "relevant_examples": [...],
    "review_suggestions": [...]
  },
  "generation_metadata": {
    "workflow_completed": true,
    "agents_used": ["researcher", "writer", "reviewer"],
    "enhanced_mode": true
  },
  "validation_result": {
    "is_valid": true,
    "issues": [],
    "warnings": [],
    "metrics": {...}
  },
  "excel_export_path": "generated_content/jenosize_content_history.xlsx"
}
```

#### 5. Interactive API Documentation
Visit `http://localhost:8000/docs` for:
- **Swagger UI**: Interactive API testing
- **Request/Response Examples**: Live examples for all endpoints
- **Parameter Validation**: Real-time validation feedback
- **Authentication**: If enabled in your setup

#### 6. Python SDK Example
```python
import requests

# Generate content via API
response = requests.post(
    "http://localhost:8000/generate",
    json={
        "topic": "Sustainable Business Practices",
        "category": "Business Strategy",
        "industry": "Manufacturing",
        "seo_keywords": ["sustainability", "green business", "ESG"],
        "content_length": "medium"
    }
)

if response.status_code == 200:
    result = response.json()
    print(f"Quality Score: {result['quality_score']}")
    print(f"Word Count: {result['metadata']['estimated_word_count']}")
    print(f"Content: {result['content'][:200]}...")
else:
    print(f"Error: {response.status_code} - {response.text}")
```

## 📊 Your Content Library

Every article you create gets saved to `generated_content/jenosize_content_history.xlsx` with:
- Full article text
- Quality scores
- Topics and keywords
- Generation timestamps
- Word counts

Perfect for tracking your content strategy!

## 🛠️ Commands You Might Need

### Cross-Platform Commands (macOS/Linux/Windows):
```bash
# Test if everything works
uv run python main.py test

# Update the AI's writing style
uv run python main.py style

# Start just the web interface
uv run python main.py frontend

# Start just the API
uv run python main.py api

# Check system health
uv run python main.py check

# Start the complete system (UI + API)
uv run python main.py full
```

### Platform-Specific Startup:

#### macOS/Linux:
```bash
# Quick start with setup script
./start.sh

# Manual restart
pkill -f "python main.py" && ./start.sh
```

#### Windows:
```powershell
# Start the system
uv run python main.py full

# Stop running processes (if needed)
taskkill /f /im python.exe
# Then restart with: uv run python main.py full

# Check if Ollama is running
curl http://localhost:11434/api/tags
```

## 🐛 Common Issues & Solutions

### Cross-Platform Issues:

**"Ollama model not found"**
```bash
ollama pull qwen3:4b-instruct-2507-q4_K_M
```

**"Generation takes too long"**
- First run is slower (AI model loading)
- Typical time: 2-3 minutes
- Check Ollama is running: visit http://localhost:11434

**Excel file not updating**
- Check the `generated_content/` folder
- Each article automatically appends to the Excel file
- Ensure write permissions in the project directory

### macOS/Linux Specific:

**"Port already in use"**
```bash
# Kill existing processes
pkill -f "python main.py"
# Or find and kill specific ports
lsof -ti:7860 | xargs kill -9
lsof -ti:8000 | xargs kill -9
```

**"Permission denied on start.sh"**
```bash
chmod +x start.sh
./start.sh
```

### Windows Specific:

**"Port already in use"**
```powershell
# Kill existing Python processes
taskkill /f /im python.exe

# Or kill specific ports
netstat -ano | findstr :7860
netstat -ano | findstr :8000
# Then kill the process: taskkill /f /pid [PID_NUMBER]
```

**"PowerShell execution policy error"**
```powershell
# Allow script execution (run as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**"uv command not found"**
```powershell
# Restart PowerShell after uv installation
# Or manually add to PATH: %USERPROFILE%\.cargo\bin
```

**"Ollama not starting automatically"**
```powershell
# Start Ollama manually
ollama serve

# Or check Windows Services for "Ollama" service
services.msc
```

**"Python/pip conflicts"**
- Use `uv` instead of `pip` for dependency management
- uv creates isolated environments automatically
- If issues persist, try: `uv clean` then `uv sync`

### General Debugging:

**Check system status:**
```bash
# Test all components
uv run python main.py check

# Check Ollama connectivity
curl http://localhost:11434/api/tags
```

**View detailed logs:**
- Check the terminal output where you started the system
- Logs are also saved in the `logs/` directory
- Look for specific error messages and stack traces

## 🎯 What You Get

### Input
```
Topic: "Digital Transformation in Retail"
Category: "Technology Trends" 
Industry: "Retail"
Keywords: "AI, customer experience, automation"
```

### Output
- **Professional 600-800 word article**
- **10/10 quality score**
- **Jenosize tone and style**
- **SEO optimized**
- **Saved to Excel automatically**
- **Ready to publish**

## 🔧 Technical Details (For Developers)

- **Language**: Python 3.9+
- **AI Model**: Qwen 3 4B (local, private)
- **Framework**: FastAPI + Gradio
- **Database**: SQLite (simple and reliable)
- **Export**: Excel via openpyxl
- **Style Learning**: TF-IDF vectorization

## 📝 Need Help?

### Quick Diagnostics:
1. **Check the logs** in the terminal where you ran the system
2. **Try the test command**: `uv run python main.py test`
3. **Check system health**: `uv run python main.py check`
4. **Verify Ollama**: `ollama list` should show your model

### Platform-Specific Restart:

#### macOS/Linux:
```bash
# Stop the system
Ctrl+C

# Restart everything
./start.sh
```

#### Windows:
```powershell
# Stop the system
Ctrl+C

# Restart everything
uv run python main.py full
```

### Getting Support:
- **Check the troubleshooting section** above for common issues
- **Visit the interactive API docs** at http://localhost:8000/docs
- **Review the logs** in the `logs/` directory
- **Test individual components** using the commands in the 🛠️ section
