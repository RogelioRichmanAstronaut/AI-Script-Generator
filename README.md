---
title: AI_Agent_Script_Builder
app_file: src/app.py
sdk: gradio
sdk_version: 5.13.1
---
# 🎓 AI Agent Script Builder

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)
[![Hugging Face Spaces](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-blue)](https://huggingface.co/spaces/rogeliorichman/AI_Script_Generator)

> Transform transcripts and PDFs into timed, structured teaching scripts using an autonomous AI agent

AI Agent Script Builder is an advanced autonomous agent that converts PDF transcripts, raw text, and conversational content into well-structured teaching scripts. It seamlessly processes inputs, extracting and analyzing the content to create organized, pedagogically scripts with time markers. Designed for educators, students, content creators, and anyone looking to transform information into clear explanations.

## 🤖 AI Agent Architecture

AI Agent Script Builder functions as a **specialized AI agent** that autonomously processes and transforms content with minimal human intervention:

### Agent Capabilities
- **Autonomous Processing**: Independently analyzes content, determines structure, and generates complete scripts
- **Decision Making**: Intelligently allocates time, prioritizes topics, and structures content based on input analysis
- **Contextual Adaptation**: Adjusts to different languages, styles, and requirements through guiding prompts
- **Obstacle Management**: Implements progressive retry strategies when facing API quota limitations
- **Goal-Oriented Operation**: Consistently works toward transforming unstructured information into coherent educational scripts

### Agent Limitations
- **Domain Specificity**: Specialized for educational script generation rather than general-purpose tasks
- **External API Dependency**: Relies on third-party language models (Gemini/OpenAI) for core reasoning
- **No Continuous Learning**: Does not improve through experience or previous interactions

This architecture enables the system to function autonomously within its specialized domain while maintaining high-quality output and resilience to common obstacles.

## 🔗 Live Demo

Try it out: [AI Agent Script Builder on Hugging Face Spaces](https://huggingface.co/spaces/rogeliorichman/AI_Script_Generator)

## ✨ Features

- 🤖 PDF transcript and raw text processing
- 🤖 AI-powered content transformation
- 📚 Structured teaching script generation
- 🔄 Coherent topic organization
- 🔌 Support for multiple AI providers (Gemini/OpenAI)
- ⏱️ Time-marked sections for pacing
- 🌐 Multilingual interface (English/Spanish) with flag selector
- 🌍 Generation in ANY language through the guiding prompt (not limited to UI languages)
- 🧠 Autonomous decision-making for content organization and pacing
- 🛡️ Self-healing capabilities with progressive retry strategies for API limitations

## Output Format

The generated scripts follow a structured format:

### Time Markers
- Each section includes time markers (e.g., `[11:45]`) to help pace delivery
- Customizable duration: From as short as 2 minutes to 60 minutes, with timing adjusted accordingly

### Structure
- Introduction with learning objectives
- Time-marked content sections
- Examples and practical applications
- Interactive elements (questions, exercises)
- Recap and key takeaways

For example:
```
[00:00] Introduction to Topic
- Learning objectives
- Key concepts overview

[11:45] Main Concept Explanation
- Detailed explanation
- Practical example
- Student interaction point

[23:30] Advanced Applications
...
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Virtual environment (recommended)
- Gemini API key (or OpenAI API key)

### Installation

```bash
# Clone the repository
git clone https://github.com/RogelioRichmanAstronaut/AI-Script-Generator.git
cd AI-Script-Generator

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (choose one API key based on your preference)
export GEMINI_API_KEY='your-gemini-api-key'  # Primary option
# OR
export OPENAI_API_KEY='your-openai-api-key'  # Alternative option

# On Windows use:
# set GEMINI_API_KEY=your-gemini-api-key
# set OPENAI_API_KEY=your-openai-api-key
```

### Usage

```bash
# Run with Python path set
PYTHONPATH=$PYTHONPATH:. python src/app.py

# Access the web interface
# Open http://localhost:7860 in your browser
```

## 🛠️ Technical Approach

### Prompt Engineering Strategy

Our system uses a sophisticated multi-stage prompting approach:

1. **Content Analysis & Chunking**
   - Smart text segmentation for handling large documents (9000+ words)
   - Contextual overlap between chunks to maintain coherence
   - Key topic and concept extraction from each segment

2. **Structure Generation**
   - Time-based sectioning (customizable from 2-60 minutes)
   - Educational flow design with clear progression
   - Integration of pedagogical elements (examples, exercises, questions)

3. **Educational Enhancement**
   - Transformation of casual content into formal teaching script
   - Addition of practical examples and case studies
   - Integration of interaction points and reflection questions
   - Time markers for pacing guidance

4. **Coherence Validation**
   - Cross-reference checking between sections
   - Verification of topic flow and progression
   - Consistency check for terminology and concepts
   - Quality assessment of educational elements

### Challenges & Solutions

1. **Context Length Management**
   - Challenge: Handling documents beyond model context limits
   - Solution: Implemented sliding window chunking with overlap
   - Result: Successfully processes documents up to 9000+ words with extensibility for more

2. **Educational Structure**
   - Challenge: Converting conversational text to teaching format
   - Solution: 
     - Structured templating system for different time formats (2-60 min)
     - Integration of pedagogical elements (examples, exercises)
     - Time-based sectioning with clear progression
   - Result: Coherent, time-marked teaching scripts with interactive elements

3. **Content Coherence**
   - Challenge: Maintaining narrative flow across chunked content
   - Solution: 
     - Contextual overlap between chunks
     - Topic tracking across sections
     - Cross-reference validation system
   - Result: Seamless content flow with consistent terminology

4. **Educational Quality**
   - Challenge: Ensuring high pedagogical value
   - Solution:
     - Integration of learning objectives
     - Strategic placement of examples and exercises
     - Addition of reflection questions
     - Time-appropriate pacing markers
   - Result: Engaging, structured learning materials

### Core Components

1. **PDF Processing**: Extracts and cleans text from PDF transcripts
2. **Text Processing**: Handles direct text input and cleans/structures it
3. **Content Analysis**: Uses AI to understand and structure the content
4. **Script Generation**: Transforms content into educational format

### Implementation Details

1. **PDF/Text Handling**
   - Robust PDF text extraction
   - Raw text input processing
   - Clean-up of extracted content

2. **AI Processing**
   - Integration with Gemini API (primary)
   - OpenAI API support (alternative)
   - Structured prompt system for consistent output

3. **Output Generation**
   - Organized teaching scripts
   - Clear section structure
   - Learning points and key concepts

### Architecture

The system follows a modular agent-based design:

- 📄 PDF/text processing module (Perception)
- 🔍 Text analysis component (Cognition)
- 🤖 AI integration layer (Decision-making)
- 📝 Output formatting system (Action)
- 🔄 Error handling system (Self-correction)

This agent architecture enables autonomous processing from raw input to final output with built-in adaptation to errors and limitations.

## 🤝 Contributing

Contributions are what make the open source community amazing! Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

## 🌟 Acknowledgments

- Special thanks to the Gemini and OpenAI teams for their amazing APIs
- Inspired by educators and communicators worldwide who make learning engaging

## 📧 Contact

Project Link: [https://github.com/RogelioRichmanAstronaut/AI-Script-Generator](https://github.com/RogelioRichmanAstronaut/AI-Script-Generator) 

## 🔮 Roadmap

- [ ] Support for multiple output formats (PDF, PPTX)
- [ ] Interactive elements generation
- [ ] Custom templating system
- [ ] Copy to clipboard button for generated content
- [x] Multilingual capabilities
  - [x] Content generation in any language via guiding prompt
  - [x] UI language support
    - [x] English
    - [x] Spanish
    - [ ] French
    - [ ] German
- [ ] Integration with LMS platforms
- [x] Timestamp toggle - ability to show/hide time markers in the output text

---

<p align="center">Made with ❤️ for educators, students, and communicators everywhere</p> 