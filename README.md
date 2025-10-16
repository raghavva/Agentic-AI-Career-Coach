# 🚀 Web Crawler AI Agent

A sophisticated AI-powered web scraping system that combines CrewAI agents with advanced crawling capabilities to extract structured data from websites. The system features a professional Streamlit frontend for career path analysis and course recommendations.

<p align="center">
  <img src="img/Snip_TEMP0001 (4).png" alt="CareerPath AI Dashboard" width="700">
</p>

You just need to upload your resume and define your career goal. The multi agentic framework collects dynamic skills in real time for existing job postings and suggests the courses needed to to work on reaching your career ambition.

## 🌟 Features

### Core Web Crawling
- **Multi-Agent Architecture**: Specialized AI agents for crawling, evaluation, and management
- **Structured Data Extraction**: Extract specific information based on custom schemas
- **Quality Assurance**: Built-in data validation and quality assessment
- **Dynamic Content Handling**: Support for JavaScript-heavy websites using Playwright

### Career Path Analysis
- **Resume Skill Extraction**: AI-powered analysis of uploaded PDF resumes
- **Career Goal Analysis**: Intelligent assessment of required skills for target roles
- **Skill Gap Identification**: Automatic comparison between current and required skills
- **Course Recommendations**: Personalized course suggestions from top platforms
- **Professional UI**: Modern, responsive Streamlit interface

<p align="center">
  <img src="img/Snip_TEMP0001 (3).png" alt="CareerPath AI Dashboard" width="700">
</p>

## 🏗️ Architecture
Agentic-AI-Career-Coach/
├── agents/ # AI Agent implementations
│ ├── CareerGoalAnalyzerAgent.py # Analyzes career requirements
│ ├── CourseFinderAgent.py # Discovers relevant courses
│ ├── EvaluatorAgent.py # Ranks and evaluates courses
│ ├── ResumeSkillExtractorAgent.py # Extracts skills from resumes
│ └── tools/ # Agent-specific tools
│ ├── analyze_resume_text.py
│ ├── course_website_crawler.py
│ └── job_website_crawler.py
├── utils/ # Utility functions
│ └── pdf_parser.py # PDF text extraction
├── front_end.py # Streamlit web interface
└── requirements.txt # Dependencies




## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key
- Playwright browsers installed

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/raghavva/Agentic-AI-Career-Coach.git
   cd Agentic-AI-Career-Coach
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Playwright browsers**
   ```bash
   playwright install
   ```

5. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

### Running the Application

#### Web Interface (Career Path Analysis)
```bash
streamlit run front_end.py
```

## 📖 Usage

### Web Interface

1. **Upload Resume**: Upload a PDF resume for skill extraction
2. **Set Career Goal**: Specify your target career role (e.g., "Data Scientist", "Cloud Engineer")
3. **Analyze**: Click "Analyze & Recommend" to get personalized insights
4. **Review Results**: View skill gaps and top 5 course recommendations


## 🛠️ Technology Stack

### AI & Machine Learning
- **CrewAI**: Multi-agent orchestration framework
- **OpenAI GPT-4**: Language model for intelligent analysis
- **LangChain**: LLM integration and prompt management

### Web Crawling & Automation
- **Crawl4AI**: Advanced web crawling with LLM integration
- **Playwright**: Browser automation for dynamic content
- **AsyncIO**: Asynchronous processing for better performance

### Web Interface
- **Streamlit**: Modern web application framework
- **Custom CSS**: Professional styling and responsive design

### Data Processing
- **PyPDF2**: PDF text extraction
- **Unstructured**: Document processing
- **JSON**: Data serialization and API responses

## 🔧 Configuration

### Agent Configuration
Modify agent behavior in `agents.py`:
- **Web Crawling Agent**: Handles data extraction
- **Evaluation Agent**: Validates data quality
- **Manager Agent**: Coordinates workflow

### Task Configuration
Customize tasks in `tasks.py`:
- Define extraction schemas
- Set quality criteria
- Configure workflow steps

### UI Customization
Edit `front_end.py` to modify:
- Styling and layout
- Additional features
- Data visualization

## 📊 How It Works

### 1. Resume Analysis
- Upload PDF resume
- AI extracts technical and soft skills
- Identifies experience level and qualifications

### 2. Career Goal Analysis
- Specify target role
- System crawls job websites (Indeed, LinkedIn)
- Analyzes current market requirements
- Identifies most frequently mentioned skills

### 3. Skill Gap Identification
- Compares current skills vs. required skills
- Highlights missing competencies
- Prioritizes skills by market demand

### 4. Course Discovery
- Crawls course platforms (Coursera, Udemy)
- Extracts course details, ratings, and pricing
- Filters courses by relevance to missing skills

### 5. Smart Evaluation
- AI evaluates course quality and relevance
- Ranks courses by multiple criteria
- Provides top 5 personalized recommendations

## 🐛 Troubleshooting

### Common Issues

1. **Playwright Installation**
   ```bash
   playwright install chromium
   ```

2. **OpenAI API Errors**
   - Verify API key in `.env` file
   - Check API quota and billing

3. **PDF Processing Issues**
   - Ensure PDF contains readable text
   - Try different PDF formats

4. **Crawling Failures**
   - Check website accessibility
   - Verify URL format
   - Review rate limiting

5. **Course Display Issues**
   - Check debug sections in frontend
   - Verify data structure from agents
   - Review error logs in terminal

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt
streamlit run front_end.py
```

## 📈 Roadmap

- [ ] Add more course platforms (edX, Pluralsight, LinkedIn Learning)
- [ ] Implement course progress tracking
- [ ] Add skill assessment quizzes
- [ ] Integrate with job application tracking
- [ ] Add social features for learning communities
- [ ] Implement advanced analytics dashboard
- [ ] Add mobile app support

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **CrewAI** for the multi-agent framework
- **Streamlit** for the web interface
- **OpenAI** for language model capabilities
- **Playwright** for browser automation
- **Crawl4AI** for advanced web crawling

## 📞 Support

For questions and support:
- Create an issue in the repository
- Check the troubleshooting section
- Review the documentation

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=raghavva/Agentic-AI-Career-Coach&type=Date)](https://star-history.com/#raghavva/Agentic-AI-Career-Coach&Date)

---

**Built with ❤️ for intelligent career development**

*Transform your career with AI-powered insights and personalized learning paths*
