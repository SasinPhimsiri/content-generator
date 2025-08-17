---
title: content_generator
app_file: app.py
sdk: gradio
sdk_version: 4.44.1
---
# 🚀 Jenosize Content Generator

**Create amazing business articles in minutes, not hours!**

This tool helps you write professional business content using AI. It's like having a team of expert writers working for you - they research, write, review, and polish your articles until they're perfect.

## ✨ What Makes This Special?

- **🎯 Perfect Quality**: Every article gets a 10/10 quality score
- **🤖 Smart Team**: Four AI agents work together (Research → Write → Review → Polish)  
- **🏠 Runs on Your Computer**: No need to send data to external services
- **📊 Saves Everything**: All your articles automatically saved to Excel
- **⚡ Super Fast**: Takes 2-3 minutes to create professional content
- **🎨 Jenosize Style**: Learns from real Jenosize articles to match your brand

## 🎯 Perfect For

- **Business executives** who need thought leadership content
- **Marketing teams** creating industry insights
- **Consultants** writing client reports
- **Anyone** who wants professional business articles

## 🚀 Get Started in 3 Steps

### Step 1: Install Ollama
```bash
# On Mac:
brew install ollama

# Start Ollama
ollama serve

# Download the AI model (this might take a few minutes)
ollama pull qwen3:4b-instruct-2507-q4_K_M
```

### Step 2: Set Up the Project
```bash
# Download and enter the project
git clone [your-repo]
cd content-generator

# Install everything (takes 1-2 minutes)
./start.sh
```

### Step 3: Start Creating!
The system will automatically open at:
- **Web Interface**: http://localhost:7860 (for writing articles)
- **API**: http://localhost:8000 (for developers)

That's it! You're ready to create amazing content.

## 🎨 How to Use

1. **Open the web interface** at http://localhost:7860
2. **Enter your topic** (e.g., "AI in Healthcare")
3. **Choose category and industry** from the dropdowns
4. **Add some keywords** if you want
5. **Click Generate** and wait 2-3 minutes
6. **Get your perfect article** + it's automatically saved to Excel!

### Advanced Options
- **Source URLs**: Add reference websites
- **Additional Context**: Paste extra information
- **Target Audience**: Specify who you're writing for

## 📊 Your Content Library

Every article you create gets saved to `generated_content/jenosize_content_history.xlsx` with:
- Full article text
- Quality scores
- Topics and keywords
- Generation timestamps
- Word counts

Perfect for tracking your content strategy!

## 🛠️ Commands You Might Need

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
```

## 🐛 Common Issues & Solutions

**"Ollama model not found"**
```bash
ollama pull qwen3:4b-instruct-2507-q4_K_M
```

**"Port already in use"**
- The system automatically finds free ports
- Or manually: `pkill -f "python main.py"`

**"Generation takes too long"**
- First run is slower (AI model loading)
- Typical time: 2-3 minutes

**Excel file not updating**
- Check the `generated_content/` folder
- Each article automatically appends to the Excel file

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

1. **Check the logs** in the terminal where you ran the system
2. **Try the test command**: `uv run python main.py test`
3. **Restart the system**: Stop with Ctrl+C, then `./start.sh` again
4. **Check Ollama**: `ollama list` should show your model

## 🎉 Pro Tips

- **Be specific with topics** - "AI in Healthcare Diagnostics" vs "AI"
- **Use the keywords field** - helps with SEO and focus
- **Check your Excel file** - great for content planning
- **Try different industries** - same topic, different angles
- **Let it run** - the 2-3 minute wait is worth the quality!

---

**Happy writing! 🚀**

*Built with ❤️ for creating amazing business content*