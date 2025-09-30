import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics import renderPDF
import io
import base64
from datetime import datetime
import json
import tempfile
import os
from PIL import Image as PILImage
import plotly.io as pio

class ExportManager:
    def __init__(self):
        self.supported_formats = {
            'pdf': 'PDF Document',
            'png': 'PNG Image', 
            'csv': 'CSV Data',
            'json': 'JSON Data',
            'html': 'HTML Report'
        }
    
    def export_progress_report(self, user_data, progress_data, format='pdf'):
        """Export user progress report"""
        if format == 'pdf':
            return self._export_progress_pdf(user_data, progress_data)
        elif format == 'csv':
            return self._export_progress_csv(progress_data)
        elif format == 'json':
            return self._export_progress_json(user_data, progress_data)
        elif format == 'html':
            return self._export_progress_html(user_data, progress_data)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def export_math_worksheet(self, problems, solutions, title="Algebra Worksheet", format='pdf'):
        """Export math problems as worksheet"""
        if format == 'pdf':
            return self._export_worksheet_pdf(problems, solutions, title)
        elif format == 'html':
            return self._export_worksheet_html(problems, solutions, title)
        else:
            raise ValueError(f"Unsupported format for worksheet: {format}")
    
    def export_visualization(self, fig, title="Math Visualization", format='png'):
        """Export plotly or matplotlib figures"""
        if format == 'png':
            return self._export_plot_png(fig, title)
        elif format == 'pdf':
            return self._export_plot_pdf(fig, title)
        elif format == 'svg':
            return self._export_plot_svg(fig, title)
        else:
            raise ValueError(f"Unsupported format for visualization: {format}")
    
    def export_formula_sheet(self, formulas, category="Algebra", format='pdf'):
        """Export formula reference sheet"""
        if format == 'pdf':
            return self._export_formulas_pdf(formulas, category)
        elif format == 'html':
            return self._export_formulas_html(formulas, category)
        else:
            raise ValueError(f"Unsupported format for formula sheet: {format}")

    # PDF Export Methods
    def _export_progress_pdf(self, user_data, progress_data):
        """Export progress report as PDF"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, 
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            textColor=colors.HexColor('#2E86AB')
        )
        
        story.append(Paragraph(f"Algebra Learning Progress Report", title_style))
        story.append(Spacer(1, 12))
        
        # User information
        story.append(Paragraph(f"<b>Student:</b> {user_data.get('username', 'N/A')}", styles['Normal']))
        story.append(Paragraph(f"<b>Report Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Progress summary
        story.append(Paragraph("<b>Progress Summary</b>", styles['Heading2']))
        
        summary_data = [
            ['Metric', 'Value'],
            ['Problems Attempted', str(progress_data.get('problems_attempted', 0))],
            ['Problems Solved', str(progress_data.get('problems_solved', 0))],
            ['Accuracy Rate', f"{progress_data.get('accuracy', 0):.1f}%"],
            ['Current Level', progress_data.get('current_level', 'N/A')],
            ['Total Points', str(progress_data.get('total_points', 0))],
            ['Study Streak', f"{progress_data.get('streak_days', 0)} days"]
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4FD1C7')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F7FAFC')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Concept mastery
        if progress_data.get('concept_mastery'):
            story.append(Paragraph("<b>Concept Mastery</b>", styles['Heading2']))
            
            concept_data = [['Concept', 'Proficiency', 'Problems Solved', 'Mastery Level']]
            for concept in progress_data['concept_mastery']:
                concept_data.append([
                    concept.get('concept', 'N/A'),
                    f"{concept.get('proficiency', 0):.1f}%",
                    str(concept.get('problems_solved', 0)),
                    concept.get('mastery_level', 'beginner').title()
                ])
            
            concept_table = Table(concept_data, colWidths=[1.5*inch, 1.2*inch, 1.5*inch, 1.3*inch])
            concept_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            
            story.append(concept_table)
            story.append(Spacer(1, 20))
        
        # Recommendations
        story.append(Paragraph("<b>Learning Recommendations</b>", styles['Heading2']))
        recommendations = progress_data.get('recommendations', [])
        if recommendations:
            for rec in recommendations[:5]:  # Top 5 recommendations
                story.append(Paragraph(f"• {rec}", styles['Normal']))
        else:
            story.append(Paragraph("• Continue practicing regularly", styles['Normal']))
            story.append(Paragraph("• Focus on weaker concepts", styles['Normal']))
            story.append(Paragraph("• Try more challenging problems", styles['Normal']))
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(Paragraph("<i>Generated by Algebra Visualizer Pro</i>", 
                             ParagraphStyle('Footer', parent=styles['Italic'], fontSize=9)))
        
        doc.build(story)
        buffer.seek(0)
        
        return buffer
    
    def _export_worksheet_pdf(self, problems, solutions, title):
        """Export worksheet as PDF"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'WorksheetTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.HexColor('#2E86AB')
        )
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 15))
        
        # Instructions
        story.append(Paragraph("<b>Instructions:</b> Solve the following algebra problems. Show your work.", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Problems
        for i, (problem, solution) in enumerate(zip(problems, solutions), 1):
            story.append(Paragraph(f"<b>Problem {i}:</b> {problem}", styles['Normal']))
            story.append(Spacer(1, 8))
            
            # Add space for work
            story.append(Paragraph("Work space:", ParagraphStyle('WorkSpace', parent=styles['Italic'], textColor=colors.grey)))
            story.append(Spacer(1, 40))  # Space for writing
            
            if solution:
                story.append(Paragraph(f"<i>Answer: {solution}</i>", 
                                     ParagraphStyle('Answer', parent=styles['Italic'], textColor=colors.green)))
            
            story.append(Spacer(1, 15))
        
        # Solutions page (if provided)
        if any(solutions):
            story.append(Paragraph("<b>Answer Key</b>", styles['Heading2']))
            for i, (problem, solution) in enumerate(zip(problems, solutions), 1):
                if solution:
                    story.append(Paragraph(f"<b>{i}.</b> {problem}", styles['Normal']))
                    story.append(Paragraph(f"<i>Solution: {solution}</i>", styles['Italic']))
                    story.append(Spacer(1, 8))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def _export_formulas_pdf(self, formulas, category):
        """Export formula reference sheet as PDF"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        story.append(Paragraph(f"{category} Formula Reference Sheet", styles['Heading1']))
        story.append(Spacer(1, 15))
        story.append(Paragraph(f"<i>Generated on {datetime.now().strftime('%Y-%m-%d')}</i>", styles['Italic']))
        story.append(Spacer(1, 20))
        
        # Formulas
        for i, formula in enumerate(formulas, 1):
            # Formula name
            story.append(Paragraph(f"<b>{formula.get('name', f'Formula {i}')}</b>", styles['Heading2']))
            
            # LaTeX formula (as text since we can't render LaTeX in reportlab easily)
            latex_formula = formula.get('latex', '')
            story.append(Paragraph(f"Formula: {latex_formula}", styles['Normal']))
            
            # Description
            if formula.get('description'):
                story.append(Paragraph(f"Description: {formula['description']}", styles['Normal']))
            
            # Example
            if formula.get('example'):
                story.append(Paragraph(f"Example: {formula['example']}", styles['Normal']))
            
            story.append(Spacer(1, 15))
        
        story.append(Paragraph("<i>Keep this reference sheet for your studies!</i>", styles['Italic']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer

    # CSV Export Methods
    def _export_progress_csv(self, progress_data):
        """Export progress data as CSV"""
        # Create DataFrame from progress data
        data = {
            'Metric': [
                'Problems Attempted',
                'Problems Solved', 
                'Accuracy Rate',
                'Total Points',
                'Current Level',
                'Study Streak (days)'
            ],
            'Value': [
                progress_data.get('problems_attempted', 0),
                progress_data.get('problems_solved', 0),
                f"{progress_data.get('accuracy', 0):.1f}%",
                progress_data.get('total_points', 0),
                progress_data.get('current_level', 'N/A'),
                progress_data.get('streak_days', 0)
            ]
        }
        
        df = pd.DataFrame(data)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        return io.BytesIO(csv_buffer.getvalue().encode())

    # JSON Export Methods  
    def _export_progress_json(self, user_data, progress_data):
        """Export progress data as JSON"""
        export_data = {
            'export_info': {
                'type': 'algebra_progress_report',
                'version': '1.0',
                'generated_at': datetime.now().isoformat(),
                'generated_by': 'Algebra Visualizer Pro'
            },
            'user_info': {
                'username': user_data.get('username'),
                'user_id': user_data.get('id')
            },
            'progress_data': progress_data
        }
        
        json_buffer = io.BytesIO()
        json_buffer.write(json.dumps(export_data, indent=2).encode())
        json_buffer.seek(0)
        return json_buffer

    # HTML Export Methods
    def _export_progress_html(self, user_data, progress_data):
        """Export progress report as HTML"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Algebra Progress Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ color: #2E86AB; border-bottom: 2px solid #4FD1C7; padding-bottom: 10px; }}
                .section {{ margin: 20px 0; }}
                .metric-card {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #4FD1C7; color: white; }}
                .recommendation {{ background: #e8f5e8; padding: 10px; margin: 5px 0; border-radius: 3px; }}
                .footer {{ margin-top: 30px; font-style: italic; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Algebra Learning Progress Report</h1>
                <p><strong>Student:</strong> {user_data.get('username', 'N/A')}</p>
                <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            </div>
            
            <div class="section">
                <h2>Progress Summary</h2>
                <div class="metric-card">
                    <p><strong>Problems Attempted:</strong> {progress_data.get('problems_attempted', 0)}</p>
                    <p><strong>Problems Solved:</strong> {progress_data.get('problems_solved', 0)}</p>
                    <p><strong>Accuracy Rate:</strong> {progress_data.get('accuracy', 0):.1f}%</p>
                    <p><strong>Total Points:</strong> {progress_data.get('total_points', 0)}</p>
                    <p><strong>Study Streak:</strong> {progress_data.get('streak_days', 0)} days</p>
                </div>
            </div>
        """
        
        # Concept mastery table
        if progress_data.get('concept_mastery'):
            html_content += """
            <div class="section">
                <h2>Concept Mastery</h2>
                <table>
                    <tr>
                        <th>Concept</th>
                        <th>Proficiency</th>
                        <th>Problems Solved</th>
                        <th>Mastery Level</th>
                    </tr>
            """
            
            for concept in progress_data['concept_mastery']:
                html_content += f"""
                    <tr>
                        <td>{concept.get('concept', 'N/A')}</td>
                        <td>{concept.get('proficiency', 0):.1f}%</td>
                        <td>{concept.get('problems_solved', 0)}</td>
                        <td>{concept.get('mastery_level', 'beginner').title()}</td>
                    </tr>
                """
            
            html_content += "</table></div>"
        
        # Recommendations
        html_content += """
            <div class="section">
                <h2>Learning Recommendations</h2>
        """
        
        recommendations = progress_data.get('recommendations', [])
        if recommendations:
            for rec in recommendations:
                html_content += f'<div class="recommendation">• {rec}</div>'
        else:
            html_content += """
                <div class="recommendation">• Continue practicing regularly</div>
                <div class="recommendation">• Focus on weaker concepts</div>
                <div class="recommendation">• Try more challenging problems</div>
            """
        
        html_content += """
            </div>
            <div class="footer">
                <p>Generated by Algebra Visualizer Pro</p>
            </div>
        </body>
        </html>
        """
        
        buffer = io.BytesIO()
        buffer.write(html_content.encode())
        buffer.seek(0)
        return buffer
    
    def _export_worksheet_html(self, problems, solutions, title):
        """Export worksheet as HTML"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                .header {{ text-align: center; color: #2E86AB; margin-bottom: 30px; }}
                .problem {{ margin: 25px 0; padding: 15px; border-left: 4px solid #4FD1C7; background: #f8f9fa; }}
                .workspace {{ min-height: 100px; border: 1px dashed #ccc; margin: 10px 0; padding: 10px; }}
                .answer {{ color: #28a745; font-style: italic; margin-top: 10px; }}
                .instructions {{ background: #e8f4f8; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{title}</h1>
                <p>Generated on {datetime.now().strftime('%Y-%m-%d')}</p>
            </div>
            
            <div class="instructions">
                <h3>Instructions:</h3>
                <p>Solve the following algebra problems. Show your work in the provided space.</p>
            </div>
        """
        
        for i, (problem, solution) in enumerate(zip(problems, solutions), 1):
            html_content += f"""
            <div class="problem">
                <h3>Problem {i}</h3>
                <p><strong>{problem}</strong></p>
                <div class="workspace">
                    <em>Show your work here...</em>
                </div>
            """
            
            if solution:
                html_content += f'<div class="answer"><strong>Answer:</strong> {solution}</div>'
            
            html_content += "</div>"
        
        html_content += """
            <div style="margin-top: 40px; font-style: italic; color: #666;">
                <p>Algebra Visualizer Pro Worksheet</p>
            </div>
        </body>
        </html>
        """
        
        buffer = io.BytesIO()
        buffer.write(html_content.encode())
        buffer.seek(0)
        return buffer
    
    def _export_formulas_html(self, formulas, category):
        """Export formula reference sheet as HTML"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{category} Formula Reference</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ text-align: center; color: #2E86AB; border-bottom: 2px solid #4FD1C7; padding-bottom: 20px; }}
                .formula {{ margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 5px; }}
                .formula-name {{ color: #2E86AB; font-weight: bold; }}
                .latex-formula {{ font-family: "Courier New", monospace; background: white; padding: 10px; margin: 10px 0; }}
                .example {{ background: #e8f5e8; padding: 10px; margin: 5px 0; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{category} Formula Reference Sheet</h1>
                <p>Generated on {datetime.now().strftime('%Y-%m-%d')}</p>
            </div>
        """
        
        for formula in formulas:
            html_content += f"""
            <div class="formula">
                <div class="formula-name">{formula.get('name', 'Formula')}</div>
                <div class="latex-formula">{formula.get('latex', '')}</div>
            """
            
            if formula.get('description'):
                html_content += f"<p>{formula['description']}</p>"
            
            if formula.get('example'):
                html_content += f'<div class="example"><strong>Example:</strong> {formula["example"]}</div>'
            
            html_content += "</div>"
        
        html_content += """
            <div style="margin-top: 40px; font-style: italic; color: #666; text-align: center;">
                <p>Algebra Visualizer Pro Formula Reference</p>
            </div>
        </body>
        </html>
        """
        
        buffer = io.BytesIO()
        buffer.write(html_content.encode())
        buffer.seek(0)
        return buffer

    # Image Export Methods
    def _export_plot_png(self, fig, title):
        """Export plot as PNG image"""
        if isinstance(fig, go.Figure):
            # Plotly figure
            img_bytes = fig.to_image(format="png", width=800, height=600)
            buffer = io.BytesIO(img_bytes)
        else:
            # Matplotlib figure
            buffer = io.BytesIO()
            fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
            plt.close(fig)
        
        buffer.seek(0)
        return buffer
    
    def _export_plot_pdf(self, fig, title):
        """Export plot as PDF"""
        buffer = io.BytesIO()
        
        if isinstance(fig, go.Figure):
            # For Plotly, convert to image first then embed in PDF
            img_buffer = self._export_plot_png(fig, title)
            img = PILImage.open(img_buffer)
            
            # Create a simple PDF with the image
            from reportlab.pdfgen import canvas
            c = canvas.Canvas(buffer, pagesize=letter)
            c.setTitle(title)
            
            # Add title
            c.setFont("Helvetica-Bold", 16)
            c.drawString(72, 750, title)
            
            # Add image (scale to fit)
            img_width, img_height = img.size
            scale = min(500/img_width, 500/img_height)
            c.drawImage(img_buffer, 72, 200, 
                       width=img_width*scale, 
                       height=img_height*scale)
            
            c.save()
        else:
            # Matplotlib figure
            fig.savefig(buffer, format='pdf', bbox_inches='tight')
            plt.close(fig)
        
        buffer.seek(0)
        return buffer
    
    def _export_plot_svg(self, fig, title):
        """Export plot as SVG"""
        buffer = io.BytesIO()
        
        if isinstance(fig, go.Figure):
            # Plotly figure
            svg_bytes = fig.to_image(format="svg")
            buffer.write(svg_bytes)
        else:
            # Matplotlib figure
            fig.savefig(buffer, format='svg', bbox_inches='tight')
            plt.close(fig)
        
        buffer.seek(0)
        return buffer

    # Utility Methods
    def get_download_link(self, buffer, filename, text="Download"):
        """Generate download link for Streamlit"""
        b64 = base64.b64encode(buffer.getvalue()).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">{text}</a>'
        return href
    
    def create_export_preview(self, content_type, data):
        """Create preview of export content"""
        if content_type == 'progress':
            return self._preview_progress_report(data)
        elif content_type == 'worksheet':
            return self._preview_worksheet(data)
        elif content_type == 'formulas':
            return self._preview_formulas(data)
        else:
            return "Preview not available for this content type."
    
    def _preview_progress_report(self, progress_data):
        """Create preview of progress report"""
        preview = f"""
        **Progress Report Preview**
        
        - Problems Solved: {progress_data.get('problems_solved', 0)}
        - Accuracy: {progress_data.get('accuracy', 0):.1f}%
        - Current Level: {progress_data.get('current_level', 'N/A')}
        - Study Streak: {progress_data.get('streak_days', 0)} days
        
        **Concepts Mastered:** {len([c for c in progress_data.get('concept_mastery', []) if c.get('proficiency', 0) >= 80])}
        """
        return preview
    
    def _preview_worksheet(self, worksheet_data):
        """Create preview of worksheet"""
        problems = worksheet_data.get('problems', [])
        preview = f"""
        **Worksheet Preview**
        
        Contains {len(problems)} problems:
        """
        
        for i, problem in enumerate(problems[:3], 1):  # Show first 3 problems
            preview += f"\n{i}. {problem}"
        
        if len(problems) > 3:
            preview += f"\n... and {len(problems) - 3} more problems"
        
        return preview
    
    def _preview_formulas(self, formulas_data):
        """Create preview of formula sheet"""
        formulas = formulas_data.get('formulas', [])
        preview = f"""
        **Formula Sheet Preview**
        
        Contains {len(formulas)} formulas:
        """
        
        for i, formula in enumerate(formulas[:5], 1):  # Show first 5 formulas
            preview += f"\n{i}. {formula.get('name', 'Unnamed Formula')}"
        
        return preview

# Streamlit UI Components for Export
def render_export_panel():
    """Render export control panel in Streamlit"""
    st.markdown("---")
    st.header("📤 Export Content")
    
    export_manager = ExportManager()
    
    # Export type selection
    export_type = st.selectbox(
        "What would you like to export?",
        ["Progress Report", "Practice Worksheet", "Formula Sheet", "Visualization"]
    )
    
    # Format selection
    export_format = st.selectbox(
        "Export format",
        list(export_manager.supported_formats.keys()),
        format_func=lambda x: export_manager.supported_formats[x]
    )
    
    # Content-specific options
    if export_type == "Progress Report":
        render_progress_export(export_manager, export_format)
    
    elif export_type == "Practice Worksheet":
        render_worksheet_export(export_manager, export_format)
    
    elif export_type == "Formula Sheet":
        render_formula_export(export_manager, export_format)
    
    elif export_type == "Visualization":
        render_visualization_export(export_manager, export_format)

def render_progress_export(export_manager, format):
    """Render progress report export interface"""
    st.subheader("Export Progress Report")
    
    # Get user progress data (this would come from your database)
    user_data = st.session_state.get('user_data', {'username': 'Student', 'id': 1})
    progress_data = st.session_state.get('progress_data', {})
    
    if not progress_data:
        st.warning("No progress data available. Complete some problems first!")
        return
    
    # Preview
    with st.expander("Preview Report"):
        preview = export_manager.create_export_preview('progress', progress_data)
        st.write(preview)
    
    # Export options
    col1, col2 = st.columns(2)
    
    with col1:
        include_recommendations = st.checkbox("Include Learning Recommendations", value=True)
        include_concept_details = st.checkbox("Include Concept Details", value=True)
    
    with col2:
        filename = st.text_input("Filename", value=f"algebra_progress_{datetime.now().strftime('%Y%m%d')}")
    
    # Export button
    if st.button("📄 Generate Progress Report", type="primary"):
        with st.spinner("Generating report..."):
            try:
                # Prepare data for export
                export_data = progress_data.copy()
                if not include_recommendations:
                    export_data.pop('recommendations', None)
                if not include_concept_details:
                    export_data.pop('concept_mastery', None)
                
                # Generate export
                buffer = export_manager.export_progress_report(user_data, export_data, format)
                
                # Create download link
                file_extension = format
                if format == 'pdf':
                    mime_type = 'application/pdf'
                elif format == 'csv':
                    mime_type = 'text/csv'
                elif format == 'json':
                    mime_type = 'application/json'
                else:
                    mime_type = 'text/html'
                
                st.success("Report generated successfully!")
                
                # Download button
                st.download_button(
                    label=f"📥 Download {format.upper()} Report",
                    data=buffer,
                    file_name=f"{filename}.{file_extension}",
                    mime=mime_type
                )
                
            except Exception as e:
                st.error(f"Error generating report: {e}")

def render_worksheet_export(export_manager, format):
    """Render worksheet export interface"""
    st.subheader("Export Practice Worksheet")
    
    # Worksheet configuration
    col1, col2 = st.columns(2)
    
    with col1:
        num_problems = st.slider("Number of Problems", 5, 20, 10)
        difficulty = st.selectbox("Difficulty Level", ["Easy", "Medium", "Hard", "Mixed"])
        include_answers = st.checkbox("Include Answer Key", value=True)
    
    with col2:
        problem_types = st.multiselect(
            "Problem Types",
            ["Quadratic Equations", "Polynomials", "Factoring", "Expansion", "Word Problems"],
            default=["Quadratic Equations", "Polynomials"]
        )
        filename = st.text_input("Filename", value=f"algebra_worksheet_{datetime.now().strftime('%Y%m%d')}")
    
    # Generate worksheet content (this would come from your problem generator)
    if st.button("🔄 Generate Worksheet Preview"):
        # Mock problems for demonstration
        mock_problems = [
            "Solve: x² + 5x + 6 = 0",
            "Expand: (2x + 3)(x - 4)",
            "Factor: x² - 9",
            "Simplify: (3x² + 2x) - (x² - 4x)",
            "Solve the system: 2x + 3y = 7, x - y = 1"
        ]
        
        mock_solutions = [
            "x = -2, -3",
            "2x² - 5x - 12", 
            "(x - 3)(x + 3)",
            "2x² + 6x",
            "x = 2, y = 1"
        ] if include_answers else [""] * len(mock_problems)
        
        st.session_state.worksheet_data = {
            'problems': mock_problems[:num_problems],
            'solutions': mock_solutions[:num_problems]
        }
    
    # Preview and export
    if 'worksheet_data' in st.session_state:
        worksheet_data = st.session_state.worksheet_data
        
        with st.expander("Worksheet Preview"):
            preview = export_manager.create_export_preview('worksheet', worksheet_data)
            st.write(preview)
            
            for i, problem in enumerate(worksheet_data['problems'][:3], 1):
                st.write(f"**{i}.** {problem}")
        
        if st.button("📝 Export Worksheet", type="primary"):
            with st.spinner("Generating worksheet..."):
                try:
                    buffer = export_manager.export_math_worksheet(
                        worksheet_data['problems'],
                        worksheet_data['solutions'] if include_answers else [],
                        f"Algebra Practice Worksheet - {difficulty}",
                        format
                    )
                    
                    st.success("Worksheet generated successfully!")
                    
                    # Download button
                    file_extension = format
                    mime_type = 'application/pdf' if format == 'pdf' else 'text/html'
                    
                    st.download_button(
                        label=f"📥 Download {format.upper()} Worksheet",
                        data=buffer,
                        file_name=f"{filename}.{file_extension}",
                        mime=mime_type
                    )
                    
                except Exception as e:
                    st.error(f"Error generating worksheet: {e}")

def render_formula_export(export_manager, format):
    """Render formula sheet export interface"""
    st.subheader("Export Formula Reference Sheet")
    
    # Formula selection
    categories = st.multiselect(
        "Select Formula Categories",
        ["Algebra Basics", "Quadratic Equations", "Polynomials", "Exponents", "Calculus"],
        default=["Algebra Basics", "Quadratic Equations"]
    )
    
    filename = st.text_input("Filename", value=f"algebra_formulas_{datetime.now().strftime('%Y%m%d')}")
    
    # Mock formulas for demonstration
    formulas = [
        {
            'name': 'Quadratic Formula',
            'latex': 'x = \\\\frac{-b \\\\pm \\\\sqrt{b^2 - 4ac}}{2a}',
            'description': 'Solves quadratic equations of form ax² + bx + c = 0',
            'example': 'For 2x² + 4x - 6 = 0, solutions are x = 1 and x = -3'
        },
        {
            'name': 'Difference of Squares',
            'latex': 'a^2 - b^2 = (a - b)(a + b)',
            'description': 'Factors the difference between two squares',
            'example': 'x² - 9 = (x - 3)(x + 3)'
        },
        {
            'name': 'Binomial Theorem',
            'latex': '(a + b)^n = \\\\sum_{k=0}^{n} \\\\binom{n}{k} a^{n-k} b^k',
            'description': 'Expands binomial expressions raised to a power',
            'example': '(x + 2)² = x² + 4x + 4'
        }
    ]
    
    with st.expander("Formula Preview"):
        preview = export_manager.create_export_preview('formulas', {'formulas': formulas})
        st.write(preview)
        
        for formula in formulas:
            st.write(f"**{formula['name']}**")
            st.latex(formula['latex'])
    
    if st.button("📚 Export Formula Sheet", type="primary"):
        with st.spinner("Generating formula sheet..."):
            try:
                buffer = export_manager.export_formula_sheet(
                    formulas,
                    "Algebra Formulas",
                    format
                )
                
                st.success("Formula sheet generated successfully!")
                
                # Download button
                file_extension = format
                mime_type = 'application/pdf' if format == 'pdf' else 'text/html'
                
                st.download_button(
                    label=f"📥 Download {format.upper()} Formula Sheet",
                    data=buffer,
                    file_name=f"{filename}.{file_extension}",
                    mime=mime_type
                )
                
            except Exception as e:
                st.error(f"Error generating formula sheet: {e}")

def render_visualization_export(export_manager, format):
    """Render visualization export interface"""
    st.subheader("Export Visualization")
    
    # This would typically export the current visualization from the app
    st.info("This feature exports the currently displayed mathematical visualization.")
    
    # For demonstration, create a sample plot
    if st.button("Generate Sample Graph"):
        # Create a sample plotly figure
        import plotly.express as px
        x = np.linspace(-10, 10, 100)
        y = x**2
        fig = px.line(x=x, y=y, title="Sample Quadratic Function: y = x²")
        st.session_state.current_visualization = fig
    
    if 'current_visualization' in st.session_state:
        st.plotly_chart(st.session_state.current_visualization)
        
        filename = st.text_input("Filename", value=f"algebra_graph_{datetime.now().strftime('%Y%m%d')}")
        
        if st.button("📊 Export Visualization", type="primary"):
            with st.spinner("Exporting visualization..."):
                try:
                    buffer = export_manager.export_visualization(
                        st.session_state.current_visualization,
                        "Algebra Visualization",
                        format
                    )
                    
                    st.success("Visualization exported successfully!")
                    
                    # Determine MIME type
                    if format == 'png':
                        mime_type = 'image/png'
                    elif format == 'pdf':
                        mime_type = 'application/pdf'
                    else:
                        mime_type = 'image/svg+xml'
                    
                    st.download_button(
                        label=f"📥 Download {format.upper()}",
                        data=buffer,
                        file_name=f"{filename}.{format}",
                        mime=mime_type
                    )
                    
                except Exception as e:
                    st.error(f"Error exporting visualization: {e}")

# Quick export buttons for common tasks
def render_quick_export_buttons():
    """Render quick export buttons for common tasks"""
    st.subheader("🚀 Quick Exports")
    
    export_manager = ExportManager()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Progress PDF", use_container_width=True):
            # Quick progress PDF export
            user_data = st.session_state.get('user_data', {'username': 'Student'})
            progress_data = st.session_state.get('progress_data', {})
            if progress_data:
                buffer = export_manager.export_progress_report(user_data, progress_data, 'pdf')
                st.download_button(
                    label="Download Progress PDF",
                    data=buffer,
                    file_name=f"progress_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
    
    with col2:
        if st.button("📝 Worksheet PDF", use_container_width=True):
            # Quick worksheet export
            mock_problems = ["Solve: x² - 4 = 0", "Expand: (x + 2)²", "Factor: x² + 6x + 9"]
            mock_solutions = ["x = ±2", "x² + 4x + 4", "(x + 3)²"]
            buffer = export_manager.export_math_worksheet(mock_problems, mock_solutions, "Quick Algebra Worksheet")
            st.download_button(
                label="Download Worksheet PDF",
                data=buffer,
                file_name=f"worksheet_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )
    
    with col3:
        if st.button("📚 Formulas PDF", use_container_width=True):
            # Quick formula sheet export
            formulas = [
                {'name': 'Quadratic Formula', 'latex': 'x = \\\\frac{-b \\\\pm \\\\sqrt{b^2 - 4ac}}{2a}'},
                {'name': 'Difference of Squares', 'latex': 'a^2 - b^2 = (a - b)(a + b)'}
            ]
            buffer = export_manager.export_formula_sheet(formulas, "Algebra Reference")
            st.download_button(
                label="Download Formula PDF",
                data=buffer,
                file_name=f"formulas_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )

# Global export manager instance
export_manager = ExportManager()

# Example usage in main app
"""
# In your main app.py, add:

from export_utils import render_export_panel, render_quick_export_buttons

# Add to your interface
render_export_panel()
render_quick_export_buttons()
"""

if __name__ == "__main__":
    # Test the export system
    st.title("📤 Export System Test")
    
    render_export_panel()
    render_quick_export_buttons()