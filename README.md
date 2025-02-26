# 🎓 AI Script Generator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

> Transform transcripts and PDFs into timed, structured teaching scripts using AI

AI Script Generator is an advanced AI system that converts PDF transcripts, raw text, and conversational content into well-structured teaching scripts. It seamlessly processes inputs, extracting and analyzing the content to create organized, pedagogically sound scripts with time markers. Designed for educators, students, content creators, and anyone looking to transform information into clear explanations.

## ✨ Features

- 🤖 PDF transcript and raw text processing
- 🤖 AI-powered content transformation
- 📚 Structured teaching script generation
- 🔄 Coherent topic organization
- 🔌 Support for multiple AI providers (Gemini/OpenAI)
- ⏱️ Time-marked sections for pacing

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

The system follows a modular design:

- 📄 PDF/text processing module
- 🔍 Text analysis component
- 🤖 AI integration layer
- 📝 Output formatting system

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

- Thanks to all contributors who have helped shape AI Script Generator
- Special thanks to the Gemini and OpenAI teams for their amazing APIs
- Inspired by educators and communicators worldwide who make learning engaging

## 📧 Contact

Project Link: [https://github.com/RogelioRichmanAstronaut/AI-Script-Generator](https://github.com/RogelioRichmanAstronaut/AI-Script-Generator) 

## 🔮 Roadmap

- [ ] Support for multiple output formats (PDF, PPTX)
- [ ] Interactive elements generation
- [ ] Custom templating system
- [ ] Multi-language support
- [ ] Integration with LMS platforms

---

<p align="center">Made with ❤️ for educators, students, and communicators everywhere</p> 