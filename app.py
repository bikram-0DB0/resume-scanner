import gradio as gr
import os
import tempfile
import shutil
from typing import List, Dict, Any, Tuple
import json

from extract_info import extract_information
from pdf_parser import extract_text_from_pdf
from utils import save_to_csv, save_to_excel

class ResumeParserApp:
    def __init__(self):
        self.processed_data = []
        self.temp_dir = None
        
    def create_temp_directory(self):
        """Create a temporary directory for processing"""
        if self.temp_dir:
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.temp_dir = tempfile.mkdtemp()
        return self.temp_dir
    
    def process_single_file(self, file_path: str, file_name: str) -> Dict[str, Any]:
        """Process a single PDF file and return extracted data"""
        try:
            text = extract_text_from_pdf(file_path)
            
            if not text or len(text.strip()) < 50:
                return {
                    'success': False,
                    'error': f'Little or no text extracted from {file_name}',
                    'data': None
                }
            
            extracted_data = extract_information(text)
            extracted_data['Resume_File'] = file_name
            
            return {
                'success': True,
                'error': None,
                'data': extracted_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error processing {file_name}: {str(e)}',
                'data': None
            }
    
    def process_files(self, files: List[Any], progress=gr.Progress()) -> Tuple[str, str, str]:
        """Process multiple PDF files"""
        if not files:
            return "❌ No files uploaded", "", ""
        
        temp_dir = self.create_temp_directory()
        
        self.processed_data = []
        successful_count = 0
        failed_count = 0
        error_messages = []
        
        progress(0, desc="Starting processing...")
        
        for i, file in enumerate(files):
            progress((i + 1) / len(files), desc=f"Processing file {i + 1}/{len(files)}")
            
            file_name = os.path.basename(file.name)
            
            result = self.process_single_file(file.name, file_name)
            
            if result['success']:
                self.processed_data.append(result['data'])
                successful_count += 1
            else:
                failed_count += 1
                error_messages.append(result['error'])
        
        total_files = len(files)
        success_rate = (successful_count / total_files) * 100 if total_files > 0 else 0
        
        summary = f"""
        📊 **Processing Summary**
        
        - **Total files processed:** {total_files}
        - **✅ Successful extractions:** {successful_count}
        - **❌ Failed extractions:** {failed_count}
        - **📈 Success rate:** {success_rate:.1f}%
        """
        
        preview = self.generate_preview()
        
        error_report = "\n".join(error_messages) if error_messages else "No errors occurred."
        
        return summary, preview, error_report
    
    def generate_preview(self) -> str:
        """Generate a preview of extracted data"""
        if not self.processed_data:
            return "No data available for preview."
        
        preview_text = "📋 **Extraction Preview**\n\n"
        
        for i, resume_data in enumerate(self.processed_data[:], 1):
            preview_text += f"**📄 Resume {i}: {resume_data.get('Resume_File', 'Unknown')}**\n\n"
            
            preview_fields = ['Name', 'Email', 'Phone', 'Skills', 'Work Experience']
            for field in preview_fields:
                value = resume_data.get(field, 'Not found')
                if value and len(str(value)) > 100:
                    value = str(value)[:100] + "..."
                preview_text += f"- **{field}:** {value}\n"
            
            preview_text += "\n" + "-" * 50 + "\n\n"
        return preview_text
    
    def download_results(self, format_type: str) -> str:
        """Generate download file"""
        if not self.processed_data:
            return None
        
        
        if format_type == "CSV":
            filename = f"resume_data.csv"
            filepath = os.path.join(self.temp_dir, filename)
            save_to_csv(self.processed_data, filepath)
            return filepath
        
        elif format_type == "Excel":
            filename = f"resume_data.xlsx"
            filepath = os.path.join(self.temp_dir, filename)
            save_to_excel(self.processed_data, filepath)
            return filepath
        
        elif format_type == "JSON":
            filename = f"resume_data.json"
            filepath = os.path.join(self.temp_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.processed_data, f, indent=2, ensure_ascii=False)
            return filepath
        
        return None
    
    def get_statistics(self) -> str:
        """Generate detailed statistics"""
        if not self.processed_data:
            return "No data available for statistics."
        
        stats_text = "📊 **Detailed Statistics**\n\n"
        
        fields = ['Name', 'Email', 'Phone', 'Skills', 'Work Experience', 
                 'Education', 'Projects', 'Hobbies', 'Qualities']
        
        stats_text += "**Field Completion Rates:**\n\n"
        for field in fields:
            completed = sum(1 for item in self.processed_data if item.get(field))
            percentage = (completed / len(self.processed_data)) * 100
            stats_text += f"- **{field}:** {completed}/{len(self.processed_data)} ({percentage:.1f}%)\n"
        
        all_skills = []
        for resume in self.processed_data:
            skills = resume.get('Skills', '')
            if skills:
                all_skills.extend([skill.strip() for skill in skills.split(',')])
        
        if all_skills:
            from collections import Counter
            top_skills = Counter(all_skills).most_common(10)
            stats_text += "\n**Top 10 Most Common Skills:**\n\n"
            for skill, count in top_skills:
                stats_text += f"- **{skill}:** {count} resumes\n"
        
        return stats_text

app = ResumeParserApp()

# UNIQUE NEON DARK THEME WITH CYBERPUNK INSPIRATION
custom_css = """
/* Import futuristic font */
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;600;700&display=swap');

* {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

.gradio-container {
    background: linear-gradient(135deg, #0a0a0a 0%, #1a0033 50%, #0a0a2a 100%);
    min-height: 100vh;
}

/* Animated gradient background */
@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.main-header {
    background: linear-gradient(135deg, #FF0066, #00F5FF, #FF0066, #7000FF);
    background-size: 300% 300%;
    animation: gradientShift 6s ease infinite;
    color: white;
    padding: 2.5rem;
    border-radius: 30px;
    margin-bottom: 2rem;
    text-align: center;
    box-shadow: 0 20px 40px rgba(0, 245, 255, 0.3), inset 0 1px 2px rgba(255,255,255,0.2);
    border: 1px solid rgba(0, 245, 255, 0.5);
    position: relative;
    overflow: hidden;
}

.main-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 1%, transparent 1%);
    background-size: 50px 50px;
    animation: shimmer 20s linear infinite;
    pointer-events: none;
}

@keyframes shimmer {
    0% { transform: translate(0, 0); }
    100% { transform: translate(50px, 50px); }
}

.main-header h1 {
    font-family: 'Orbitron', monospace;
    font-size: 3em;
    font-weight: 900;
    text-shadow: 0 0 20px rgba(0, 245, 255, 0.8), 0 0 40px rgba(255, 0, 102, 0.6);
    letter-spacing: 3px;
    animation: textGlow 2s ease-in-out infinite alternate;
}

@keyframes textGlow {
    from { text-shadow: 0 0 20px rgba(0, 245, 255, 0.8); }
    to { text-shadow: 0 0 40px rgba(255, 0, 102, 0.8), 0 0 60px rgba(0, 245, 255, 0.6); }
}

.main-header p {
    font-size: 1.2em;
    letter-spacing: 2px;
    font-weight: 300;
}

/* Neon card styles */
.cyber-card {
    background: rgba(10, 10, 30, 0.7);
    backdrop-filter: blur(10px);
    border: 2px solid;
    border-image: linear-gradient(135deg, #FF0066, #00F5FF) 1;
    border-radius: 20px;
    padding: 1.8rem;
    margin: 1rem 0;
    position: relative;
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.cyber-card::before {
    content: '';
    position: absolute;
    top: -2px;
    left: -2px;
    right: -2px;
    bottom: -2px;
    background: linear-gradient(135deg, #FF0066, #00F5FF, #FF0066);
    border-radius: 20px;
    opacity: 0;
    z-index: -1;
    transition: opacity 0.4s ease;
}

.cyber-card:hover {
    transform: translateY(-10px) scale(1.02);
    box-shadow: 0 20px 40px rgba(0, 245, 255, 0.3);
}

.cyber-card:hover::before {
    opacity: 0.3;
}

.cyber-card h3 {
    font-family: 'Orbitron', monospace;
    background: linear-gradient(135deg, #FF0066, #00F5FF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 700;
    font-size: 1.4em;
    margin-bottom: 1rem;
}

.cyber-card ul {
    list-style: none;
    padding: 0;
}

.cyber-card li {
    color: #e0e0ff;
    font-weight: 500;
    margin: 0.7rem 0;
    padding-left: 1.5rem;
    position: relative;
}

.cyber-card li:before {
    content: "➤";
    position: absolute;
    left: 0;
    color: #00F5FF;
    font-weight: bold;
    text-shadow: 0 0 5px #00F5FF;
}

/* Tabs styling */
.tabs {
    border: none !important;
}

tab-nav {
    background: rgba(0, 0, 0, 0.5) !important;
    backdrop-filter: blur(10px);
    border-radius: 15px !important;
    padding: 5px !important;
}

button[role="tab"] {
    background: transparent !important;
    color: #aaa !important;
    font-family: 'Orbitron', monospace !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
    border-radius: 10px !important;
    margin: 0 5px !important;
}

button[role="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, #FF0066, #7000FF) !important;
    color: white !important;
    box-shadow: 0 0 15px rgba(255, 0, 102, 0.5) !important;
}

/* Upload area - unique holographic design */
.upload-area {
    background: linear-gradient(135deg, rgba(255, 0, 102, 0.1), rgba(0, 245, 255, 0.1)) !important;
    border: 2px solid !important;
    border-image: linear-gradient(135deg, #FF0066, #00F5FF) 1 !important;
    border-radius: 25px !important;
    padding: 3rem 2rem !important;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: all 0.4s ease;
}

.upload-area::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.05) 1%, transparent 1%);
    background-size: 30px 30px;
    animation: hologram 15s linear infinite;
}

@keyframes hologram {
    0% { transform: translate(0, 0); }
    100% { transform: translate(100px, 100px); }
}

.upload-area:hover {
    transform: scale(1.02);
    box-shadow: 0 0 30px rgba(0, 245, 255, 0.4);
    border-color: #00F5FF !important;
}

.upload-area * {
    position: relative;
    z-index: 1;
}

.upload-area label {
    font-family: 'Orbitron', monospace !important;
    font-size: 1.2em !important;
    font-weight: 700 !important;
    background: linear-gradient(135deg, #FF0066, #00F5FF);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* Button styles - futuristic */
.gr-button {
    background: linear-gradient(135deg, #FF0066, #7000FF) !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 12px 30px !important;
    font-family: 'Orbitron', monospace !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 2px !important;
    transition: all 0.3s ease !important;
    position: relative !important;
    overflow: hidden !important;
}

.gr-button::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    border-radius: 50%;
    background: rgba(255,255,255,0.3);
    transform: translate(-50%, -50%);
    transition: width 0.6s, height 0.6s;
}

.gr-button:hover::before {
    width: 300px;
    height: 300px;
}

.gr-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 20px rgba(255, 0, 102, 0.4);
}

/* Markdown containers with neon glow */
.markdown-text {
    background: rgba(0, 0, 0, 0.4);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 20px;
    border: 1px solid rgba(0, 245, 255, 0.3);
    color: #e0e0ff;
}

/* Dropdown styling */
.gr-dropdown {
    background: rgba(10, 10, 30, 0.8) !important;
    border: 2px solid #FF0066 !important;
    border-radius: 10px !important;
    color: #00F5FF !important;
}

/* File component styling */
.gr-file {
    background: transparent !important;
}

/* Progress bar animation */
.gr-progress {
    background: rgba(255, 255, 255, 0.1) !important;
}

.gr-progress-bar {
    background: linear-gradient(90deg, #FF0066, #00F5FF, #FF0066) !important;
    background-size: 200% 100% !important;
    animation: progressGradient 1.5s linear infinite !important;
}

@keyframes progressGradient {
    0% { background-position: 0% 50%; }
    100% { background-position: 200% 50%; }
}

/* Scrollbar styling */
::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}

::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.3);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #FF0066, #00F5FF);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #00F5FF, #FF0066);
}

/* Input fields */
.gr-textbox, .gr-textarea {
    background: rgba(0, 0, 0, 0.5) !important;
    border: 2px solid #00F5FF !important;
    color: #00F5FF !important;
    border-radius: 10px !important;
}

/* Alert/message styling */
.gr-alert {
    background: rgba(0, 0, 0, 0.7) !important;
    backdrop-filter: blur(10px);
    border: 1px solid #FF0066 !important;
    color: #00F5FF !important;
}

/* Footer styling */
.footer {
    text-align: center;
    margin-top: 2rem;
    padding: 1.5rem;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    border: 1px solid rgba(0, 245, 255, 0.3);
}
"""

def create_interface():
    with gr.Blocks(css=custom_css, title="⚡ NEON PARSER | AI Resume Intelligence", theme=gr.themes.Soft()) as demo:
        
        gr.HTML("""
        <div class="main-header">
            <h1>⚡ RESUME SCANNER</h1>
            <p>AI-Powered Resume Intelligence | Cyberpunk Edition</p>
            <div style="font-size: 0.8em; margin-top: 10px; opacity: 0.8;">
                █▓▒░ Advanced Neural Extraction ░▒▓█
            </div>
        </div>
        """)
        
        with gr.Tabs(elem_classes="tabs"):
            
            with gr.TabItem("🚀 UPLOAD & PROCESS", elem_id="upload-tab"):
                with gr.Row(equal_height=False):
                    with gr.Column(scale=2):
                        gr.HTML("""
                        <div class="cyber-card">
                            <h3>⚡ OPERATION PROTOCOL</h3>
                            <ul>
                                <li>UPLOAD TARGET FILES (PDF FORMAT)</li>
                                <li>INITIATE EXTRACTION SEQUENCE</li>
                                <li>ANALYZE EXTRACTED DATA</li>
                                <li>EXPORT IN MULTIPLE FORMATS</li>
                            </ul>
                            <div style="margin-top: 15px; font-size: 0.9em; color: #00F5FF;">
                                ⚠️ OPTIMAL RESULTS WITH SELECTABLE TEXT
                            </div>
                        </div>
                        """)
                        
                        file_upload = gr.File(
                            label="📎 DEPLOY PDF FILES",
                            file_count="multiple",
                            file_types=[".pdf"],
                            elem_classes="upload-area"
                        )
                        
                        with gr.Row():
                            process_btn = gr.Button(
                                "🔥 INITIATE PROCESSING", 
                                variant="primary", 
                                size="lg"
                            )
                            clear_btn = gr.Button(
                                "🗑️ PURGE SYSTEM", 
                                variant="secondary"
                            )
                    
                    with gr.Column(scale=1):
                        gr.HTML("""
                        <div class="cyber-card">
                            <h3>✨ SYSTEM CAPABILITIES</h3>
                            <ul>
                                <li>🧠 NEURAL TEXT EXTRACTION</li>
                                <li>📊 STRUCTURED DATA OUTPUT</li>
                                <li>⚡ REAL-TIME PROCESSING</li>
                                <li>💾 MULTI-FORMAT EXPORT</li>
                                <li>📈 ADVANCED ANALYTICS</li>
                                <li>🔒 ENCRYPTED PROCESSING</li>
                            </ul>
                            <div style="margin-top: 15px; font-size: 0.85em; color: #FF0066; text-align: center;">
                                [ VERIFIED SECURE ]
                            </div>
                        </div>
                        """)
                
                with gr.Row():
                    with gr.Column():
                        summary_output = gr.Markdown(label="📊 PROCESSING REPORT", elem_classes="markdown-text")
                        
            with gr.TabItem("📊 DATA PREVIEW", elem_id="results-tab"):
                with gr.Row():
                    with gr.Column(scale=2):
                        preview_output = gr.Markdown(
                            label="🔍 EXTRACTION PREVIEW",
                            value="⚡ AWAITING DATA UPLOAD...",
                            elem_classes="markdown-text"
                        )
                    
                    with gr.Column(scale=1):
                        with gr.Group():
                            gr.HTML("""
                            <div class="cyber-card" style="text-align: center;">
                                <h3>📥 EXPORT INTERFACE</h3>
                                <div style="font-size: 2em; margin: 10px 0;">⬇️</div>
                            </div>
                            """)
                            
                            format_dropdown = gr.Dropdown(
                                choices=["CSV", "Excel", "JSON"],
                                value="Excel",
                                label="SELECT OUTPUT FORMAT"
                            )
                            
                            download_btn = gr.Button(
                                "💾 GENERATE EXPORT",
                                variant="primary"
                            )
                            
                            download_file = gr.File(
                                label="DOWNLOAD READY",
                                visible=False
                            )
            
            with gr.TabItem("📈 ADVANCED STATISTICS", elem_id="stats-tab"):
                with gr.Row():
                    with gr.Column():
                        stats_output = gr.Markdown(
                            label="📊 QUANTUM ANALYSIS",
                            value="⚡ PROCESS RESUMES TO GENERATE STATISTICS...",
                            elem_classes="markdown-text"
                        )
                        
                        refresh_stats_btn = gr.Button(
                            "🔄 REFRESH DATA MATRIX",
                            variant="secondary"
                        )
            
            with gr.TabItem("⚠️ ERROR LOG", elem_id="error-tab"):
                error_output = gr.Markdown(
                    label="🔴 SYSTEM LOGS",
                    value="✅ ALL SYSTEMS OPERATIONAL",
                    elem_classes="markdown-text"
                )
        
        gr.HTML("""
        <div class="footer">
            <div style="font-family: 'Orbitron', monospace; letter-spacing: 2px;">
                ⚡ POWERED BY ADVANCED AI ALGORITHMS | ENTERPRISE-GRADE SECURITY ⚡
            </div>
            <div style="font-size: 0.8em; margin-top: 10px; opacity: 0.6;">
                █▓▒░ VERSION 2.0 | QUANTUM PARSING ENGINE ░▒▓█
            </div>
        </div>
        """)
        
        # Event handlers
        process_btn.click(
            fn=app.process_files,
            inputs=[file_upload],
            outputs=[summary_output, preview_output, error_output],
            show_progress=True
        )
        
        download_btn.click(
            fn=lambda format_type: app.download_results(format_type),
            inputs=[format_dropdown],
            outputs=[download_file]
        ).then(
            fn=lambda x: gr.File(visible=True if x else False),
            inputs=[download_file],
            outputs=[download_file]
        )
        
        refresh_stats_btn.click(
            fn=app.get_statistics,
            outputs=[stats_output]
        )
        
        clear_btn.click(
            fn=lambda: (None, "⚡ AWAITING DATA UPLOAD...", "✅ ALL SYSTEMS OPERATIONAL", "⚡ PROCESS RESUMES TO GENERATE STATISTICS..."),
            outputs=[file_upload, preview_output, error_output, stats_output]
        )
        
        process_btn.click(
            fn=app.get_statistics,
            outputs=[stats_output]
        )
    
    return demo

if __name__ == "__main__":
    demo = create_interface()
    
    demo.launch(
        server_name="0.0.0.0",  
        server_port=7860,       
        share=True,            
        debug=True,             
        show_error=True,       
        inbrowser=True,         
        favicon_path=None,      
        ssl_verify=False        
    )