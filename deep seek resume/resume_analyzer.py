import streamlit as st
import re
import PyPDF2
from typing import Dict, List
from docx import Document

# Streamlit page config
st.set_page_config(page_title="Resume Analyzer Pro", page_icon="💼", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    .section-card {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    .recommendation-box {
        background-color: #fff7e6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffa500;
        margin: 0.5rem 0;
    }
    .video-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

class ResumeAnalyzer:
    def __init__(self):
        self.keyword_categories = {
            'technical_skills': ['python', 'java', 'javascript', 'sql', 'html', 'css', 'react', 'git', 'aws'],
            'soft_skills': ['communication', 'leadership', 'teamwork', 'problem solving', 'time management'],
            'action_verbs': ['developed', 'managed', 'implemented', 'created', 'led', 'analyzed']
        }
    
    def extract_text_from_file(self, uploaded_file) -> str:
        """Extract text from uploaded PDF, DOCX, or TXT file"""
        text = ""
        
        if uploaded_file.type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
                
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = Document(uploaded_file)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
                
        else:  # Assume text file
            text = str(uploaded_file.read(), "utf-8")
            
        return text.strip()
    
    def analyze_resume_content(self, text: str) -> Dict:
        analysis = {}
        analysis['word_count'] = len(text.split())
        sections = self.detect_sections(text)
        analysis['sections_found'] = sections
        analysis['missing_sections'] = self.find_missing_sections(sections)
        analysis['keyword_scores'] = self.analyze_keywords(text)
        analysis['contact_info'] = self.extract_contact_info(text)
        analysis['overall_score'] = self.calculate_overall_score(analysis)
        return analysis
    
    def detect_sections(self, text: str) -> List[str]:
        sections = []
        text_lower = text.lower()
        section_patterns = {
            'contact_info': r'(contact|phone|email|address)',
            'experience': r'(experience|work history|employment)',
            'education': r'(education|academic)',
            'skills': r'(skills|technical skills)',
            'projects': r'(projects|portfolio)'
        }
        for section, pattern in section_patterns.items():
            if re.search(pattern, text_lower): 
                sections.append(section)
        return sections
    
    def find_missing_sections(self, found_sections: List[str]) -> List[str]:
        important_sections = ['contact_info', 'experience', 'education', 'skills']
        return [section for section in important_sections if section not in found_sections]
    
    def analyze_keywords(self, text: str) -> Dict:
        text_lower = text.lower()
        scores = {}
        for category, keywords in self.keyword_categories.items():
            found_keywords = [kw for kw in keywords if kw in text_lower]
            coverage = (len(found_keywords) / len(keywords)) * 100 if keywords else 0
            scores[category] = {
                'coverage_percentage': round(coverage, 2), 
                'found_keywords': found_keywords,
                'missing_keywords': [kw for kw in keywords if kw not in found_keywords]
            }
        return scores
    
    def extract_contact_info(self, text: str) -> Dict:
        contact = {}
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        contact['email'] = emails[0] if emails else None
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        contact['phone'] = phones[0] if phones else None
        return contact
    
    def calculate_overall_score(self, analysis: Dict) -> float:
        score = (len(analysis['sections_found']) / 5) * 30
        keyword_score = sum(cat['coverage_percentage'] for cat in analysis['keyword_scores'].values()) / 3 * 0.4
        score += keyword_score
        contact_score = 10 if any(analysis['contact_info'].values()) else 0
        score += contact_score
        return round(min(100, score), 2)
    
    def generate_recommendations(self, analysis: Dict) -> List[str]:
        recommendations = []
        for missing_section in analysis['missing_sections']:
            recommendations.append(f"Add '{missing_section.replace('_', ' ').title()}' section")
        for category, score in analysis['keyword_scores'].items():
            if score['coverage_percentage'] < 50:
                missing = ', '.join(score['missing_keywords'][:3])
                recommendations.append(f"Add more {category.replace('_', ' ')} like: {missing}")
        if not analysis['contact_info']['email']:
            recommendations.append("Add professional email address")
        if not analysis['contact_info']['phone']:
            recommendations.append("Add phone number")
        return recommendations

# Enhanced UI
st.markdown('<h1 class="main-header">💼 Resume Analyzer Pro</h1>', unsafe_allow_html=True)

# Header with description
col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.markdown("""
    <div style='text-align: center; color: #666; margin-bottom: 2rem;'>
        <h3>Get AI-powered insights to optimize your resume and land more interviews</h3>
    </div>
    """, unsafe_allow_html=True)

# File upload section with better styling
st.markdown("### 📁 Upload Your Resume")
uploaded_file = st.file_uploader("", type=['pdf', 'docx', 'txt'], 
                                help="Supported formats: PDF, DOCX, TXT")

if uploaded_file is not None:
    # Analyze button with better styling
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("🚀 Analyze My Resume", use_container_width=True):
            with st.spinner("🔍 Analyzing your resume content..."):
                try:
                    analyzer = ResumeAnalyzer()
                    
                    # Extract text from file
                    text = analyzer.extract_text_from_file(uploaded_file)
                    
                    if not text.strip():
                        st.error("❌ Could not extract text from the file. Please try another file.")
                    else:
                        # Analyze resume
                        analysis = analyzer.analyze_resume_content(text)
                        recommendations = analyzer.generate_recommendations(analysis)
                        
                        # Success message
                        st.balloons()
                        st.success("✅ Analysis Complete! Here's your resume report:")
                        
                        # Main metrics in cards
                        st.markdown("## 📊 Resume Overview")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            score = analysis['overall_score']
                            if score >= 80:
                                st.markdown(f"""
                                <div class="metric-card">
                                    <h3>Overall Score</h3>
                                    <h2 style='color: #00cc66;'>{score}/100 🎉</h2>
                                    <p>Excellent! Your resume is well-optimized</p>
                                </div>
                                """, unsafe_allow_html=True)
                            elif score >= 60:
                                st.markdown(f"""
                                <div class="metric-card">
                                    <h3>Overall Score</h3>
                                    <h2 style='color: #ffa500;'>{score}/100 👍</h2>
                                    <p>Good! Some improvements needed</p>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                <div class="metric-card">
                                    <h3>Overall Score</h3>
                                    <h2 style='color: #ff4b4b;'>{score}/100 💡</h2>
                                    <p>Needs significant improvements</p>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown(f"""
                            <div class="metric-card">
                                <h3>Word Count</h3>
                                <h2 style='color: #1f77b4;'>{analysis['word_count']}</h2>
                                <p>Optimal: 400-600 words</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col3:
                            sections_found = len(analysis['sections_found'])
                            st.markdown(f"""
                            <div class="metric-card">
                                <h3>Sections Found</h3>
                                <h2 style='color: #1f77b4;'>{sections_found}/5</h2>
                                <p>Key resume sections</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Detailed Analysis in two columns
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("### 📑 Section Analysis")
                            for section in analysis['sections_found']:
                                st.markdown(f"""
                                <div class="section-card">
                                    ✅ <strong>{section.replace('_', ' ').title()}</strong>
                                </div>
                                """, unsafe_allow_html=True)
                            for section in analysis['missing_sections']:
                                st.markdown(f"""
                                <div class="section-card" style='border-left: 4px solid #ff4b4b;'>
                                    ❌ <strong>{section.replace('_', ' ').title()}</strong>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            st.markdown("### 📞 Contact Information")
                            contact = analysis['contact_info']
                            st.markdown(f"""
                            <div class="section-card">
                                📧 Email: {'✅ ' + contact['email'] if contact['email'] else '❌ Missing'}
                            </div>
                            <div class="section-card">
                                📞 Phone: {'✅ ' + contact['phone'] if contact['phone'] else '❌ Missing'}
                            </div>
                            """, unsafe_allow_html=True)
                            
                        with col2:
                            st.markdown("### 🔑 Keyword Analysis")
                            for category, scores in analysis['keyword_scores'].items():
                                percentage = scores['coverage_percentage']
                                st.markdown(f"""
                                <div class="section-card">
                                    <strong>{category.replace('_', ' ').title()}</strong>
                                    <br>Coverage: {percentage}%
                                </div>
                                """, unsafe_allow_html=True)
                                st.progress(percentage/100)
                        
                        # Recommendations in styled boxes
                        st.markdown("### 💡 Improvement Recommendations")
                        for i, rec in enumerate(recommendations, 1):
                            st.markdown(f"""
                            <div class="recommendation-box">
                                <strong>{i}. {rec}</strong>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Video section with better styling
                        st.markdown("""
                        <div class="video-container">
                            <h3>🎬 Watch This to Improve Your Resume</h3>
                            <p>Learn professional resume writing techniques</p>
                        </div>
                        """, unsafe_allow_html=True)
                        st.video("https://youtu.be/Gsjt1K3SOkY")
                        
                except Exception as e:
                    st.error(f"❌ Error analyzing resume: {str(e)}")
else:
    # Welcome state with better styling
    st.markdown("""
    <div style='text-align: center; padding: 4rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white;'>
        <h2>🚀 Ready to Optimize Your Resume?</h2>
        <p style='font-size: 1.2rem;'>Upload your resume above to get started</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Resume Analyzer Pro • Powered by AI • Get more interviews</p>
</div>
""", unsafe_allow_html=True)