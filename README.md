---
title: AI Lecture Forge
emoji: 📚
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.0.0
app_file: src/app.py
pinned: false
---

# AI Lecture Forge

🏆 Production-ready AI system for transforming conversational transcripts into structured teaching material.

## Overview

AI Lecture Forge is a state-of-the-art system that leverages multiple AI models to transform raw transcripts into professional teaching materials. It supports both local inference and API-based models, with optional Text-to-Speech capabilities.

## Key Features

### Multiple AI Models
- **Local Models** (No API key required):
  - Microsoft Phi-4 (default)
  - NovaSky Sky-T1-32B
  - DeepSeek V3
- **OpenAI Models** (API key required):
  - Default: gpt-4o-mini
  - Supports all OpenAI models
- **Google Models** (API key required):
  - Default: gemini-2.0-flash-exp
  - Supports all Gemini models

### Text-to-Speech (Optional)
- Kokoro-82M voice synthesis
- High-quality audio generation
- Multiple voice options

### Core Features
- PDF transcript processing
- Customizable lecture duration (30-60 minutes)
- Practical examples integration
- Structured output with sections
- Real-time processing

## Technologies Used

- **Python 3.8+**
- **PyTorch + Transformers**: Local inference with multiple models
  - Microsoft Phi-4 (default)
  - NovaSky Sky-T1-32B
  - DeepSeek V3
- **Text-to-Speech**: Kokoro-82M for voice generation
- **Gradio 4.0.0**: Web interface framework
- **OpenAI API** (optional): Multiple models
  - Default: gpt-4o-mini
  - Supports all OpenAI models
- **Google Gemini API** (optional): Multiple models
  - Default: gemini-2.0-flash-exp
  - Supports all Gemini models
- **PyPDF2**: PDF processing
- **python-dotenv**: Environment management
- **tiktoken**: Token counting for OpenAI
- **tqdm**: Progress bars
- **numpy**: Numerical operations

## Quick Start

### Local Development
```bash
# Clone repository
git clone [repository-url]
cd ai-lecture-forge

# Install dependencies
pip install -r requirements.txt

# Optional: Configure API keys
# Create .env file if using API models
touch .env
echo "OPENAI_API_KEY=your_key" >> .env
echo "GOOGLE_API_KEY=your_key" >> .env

# Run application
python src/app.py
```

### Hugging Face Spaces Deployment
1. Create new Space
   - Select SDK: Gradio
   - Hardware: T4 GPU (recommended)
2. Connect repository
3. Optional: Add API keys in Settings
   - OPENAI_API_KEY (if using OpenAI models)
   - GOOGLE_API_KEY (if using Gemini models)

## API Keys Configuration

There are two ways to provide API keys:

### 1. Through Web Interface (Recommended)
When using API models, the interface will show secure input fields for:
- OpenAI API Key (when using OpenAI models)
- Gemini API Key (when using Gemini models)

This is the recommended method for:
- Public deployments
- Hugging Face Spaces
- Shared instances

### 2. Using Environment Variables
For local development or private deployments:
```env
# Optional: Create .env file
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_gemini_key
```

Note: If both methods are used, keys provided through the interface take precedence.

## Environment Configuration

The `.env` file is optional and only required when using API-based models:

```env
# Required for OpenAI models
OPENAI_API_KEY=your_openai_key

# Required for Gemini models
GOOGLE_API_KEY=your_gemini_key
```

Note: Local models (Phi-4, Sky-T1-32B, DeepSeek V3) work without any API keys.

## Model Selection Guide

### Local Models
- Best for: Development, testing, offline use
- No API costs
- GPU recommended for better performance

### API Models
- Best for: Production, high-quality output
- Requires API keys
- Pay-per-use pricing

### TTS Integration
- Optional feature
- Adds voice synthesis capability
- Uses Kokoro-82M model

## Performance Considerations

- GPU recommended for local models
- T4 GPU or better for optimal performance
- CPU-only mode available but slower
- API models not affected by hardware

## Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License
MIT License - See [LICENSE](LICENSE) for details.

## Competition & Production Use
This project is designed for production environments and competitive scenarios:
- Production-ready error handling
- Scalable architecture
- Multiple model fallbacks
- Comprehensive logging
- Performance optimization 