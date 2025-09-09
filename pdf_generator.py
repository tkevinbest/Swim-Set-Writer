"""
PDF Generator for swim workout files
"""

import os
from typing import List
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from parse import PracticeSet, SetItem, WorkoutSummary, WorkoutConfig, GroupVariation

class PDFWorkoutGenerator:
    """Generate PDF documents from parsed workout data"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Set up custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='WorkoutTitle',
            parent=self.styles['Title'],
            fontSize=20,
            spaceAfter=0.3*inch,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Set header style
        self.styles.add(ParagraphStyle(
            name='SetHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=0.1*inch,
            spaceBefore=0.2*inch,
            textColor=colors.darkblue,
            borderWidth=1,
            borderColor=colors.darkblue,
            borderPadding=3,
            wordWrap='CJK'  # Ensure text wraps properly
        ))
        
        # Set item style
        self.styles.add(ParagraphStyle(
            name='SetItem',
            parent=self.styles['Normal'],
            fontSize=12,
            leftIndent=0.3*inch,
            spaceAfter=0.05*inch
        ))
        
        # Summary style
        self.styles.add(ParagraphStyle(
            name='Summary',
            parent=self.styles['Normal'],
            fontSize=11,
            alignment=TA_CENTER,
            textColor=colors.gray,
            fontName='Helvetica',
            spaceBefore=0.1*inch
        ))

        # Grand summary style
        self.styles.add(ParagraphStyle(
            name='GrandSummary',
            parent=self.styles['Normal'],
            fontSize=14,
            alignment=TA_CENTER,
            textColor=colors.darkgreen,
            fontName='Helvetica-Bold'
        ))

        # Repeat note style
        self.styles.add(ParagraphStyle(
            name='Repeat',
            parent=self.styles['Normal'],
            fontSize=12,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            leftIndent=0.6*inch  # Professional indentation
        ))
    
    def generate_pdf(self, config: WorkoutConfig, sets: List[PracticeSet], output_filename: str, title: str = None):
        """Generate a PDF from workout sets with separate pages for each group"""
        
        # Use title from config if not provided, prioritize config.title
        if title is None:
            title = config.title or "Swim Workout"
        elif config.title:
            # If config has a title, use that instead of filename-derived title
            title = config.title
        
        # Create document with metadata
        doc = SimpleDocTemplate(
            output_filename,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=1*inch,
            title=title,
            author=config.author or "Swim Practice Generator",
            subject=config.description or "Swimming Workout"
        )
        
        # Get all groups in the workout
        workout = WorkoutSummary(config, sets)
        all_groups = workout.get_all_groups()
        
        # Build story (content)
        story = []
        
        # Generate a separate page for each group
        for i, group in enumerate(all_groups):
            if i > 0:  # Add page break between groups
                story.append(PageBreak())
            
            # Add group-specific content
            story.extend(self._generate_group_page(config, sets, group, title))
        
        # Build PDF
        doc.build(story)
        print(f"PDF generated: {output_filename}")
    
    def _generate_group_page(self, config: WorkoutConfig, sets: List[PracticeSet], group: str, title: str) -> List:
        """Generate content for a specific group page"""
        page_content = []
        
        # Title without group in main title
        page_content.append(Paragraph(title, self.styles['WorkoutTitle']))
        
        # Metadata information
        metadata_lines = []
        if config.author:
            metadata_lines.append(f"<b>Coach:</b> {config.author}")
        if config.date:
            metadata_lines.append(f"<b>Date:</b> {config.date}")
        if config.level:
            metadata_lines.append(f"<b>Level:</b> {config.level}")
        if config.description:
            metadata_lines.append(f"<b>Description:</b> {config.description}")
        
        metadata_lines.append(f"<b>Units:</b> {config.units.title()}")
        metadata_lines.append(f"<b>Group:</b> {group.upper()}")
        
        # Add metadata as a single paragraph
        if metadata_lines:
            metadata_text = " | ".join(metadata_lines)
            page_content.append(Paragraph(metadata_text, self.styles['Normal']))
            page_content.append(Spacer(1, 0.2*inch))
        
        # Process each set for this group
        for set_ in sets:
            # Set header without repetition count
            set_header = f"{set_.name}"
            if set_.note:
                set_header += f" <font color='gray' size='12'><i>({set_.note})</i></font>"
            
            page_content.append(Paragraph(set_header, self.styles['SetHeader']))
            
            # Add repetition multiplier if repeated
            if set_.repeat > 1:
                multiplier_text = f"<b>{set_.repeat}x:</b>"
                page_content.append(Paragraph(multiplier_text, self.styles['Repeat']))
            
            # Set items for this group
            set_data = []
            for item in set_.items:
                # Get the variation for this group
                variation = item.get_variation_for_group(group)
                
                # Format the item for this group
                rep_str = f"{variation.reps}x" if variation.reps > 1 else ""
                interval_str = f" on {'/'.join(variation.intervals)}" if variation.intervals else ""
                # Fix comment rendering with proper HTML formatting for ReportLab
                note_str = f" <font color='gray' size='10'><i>({item.note})</i></font>" if item.note else ""
                
                item_text = f"{rep_str}{variation.distance} {variation.desc}{interval_str}{note_str}"
            
                distance_text = f"{item.total_distance(group)} {config.unit_symbol}"
                set_data.append([item_text, distance_text])
            
            # Create table for set items using Paragraphs for HTML formatting
            if set_data:
                # Convert text to Paragraphs to support HTML formatting
                formatted_data = []
                for item_text, distance_text in set_data:
                    formatted_data.append([
                        Paragraph(item_text, self.styles['SetItem']),
                        distance_text
                    ])
                
                table = Table(formatted_data, colWidths=[5*inch, 1*inch])
                table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                    ('FONTSIZE', (1, 0), (1, -1), 12),
                    ('LEFTPADDING', (0, 0), (-1, -1), 15),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                page_content.append(table)
            
            # Set total for this group (distance and time)
            set_time = set_.total_time_seconds(group)
            time_str = self._format_time_for_pdf(set_time)
            set_total = f"Distance: {set_.total_distance(group)} {config.unit_symbol}, Duration: {time_str}"
            page_content.append(Paragraph(set_total, self.styles['Summary']))
            page_content.append(Spacer(1, 0.15*inch))
        
        # Workout total for this group (distance and time)
        workout = WorkoutSummary(config, sets)
        workout_time = workout.total_time_seconds(group)
        workout_time_str = self._format_time_for_pdf(workout_time)
        total_text = f"WORKOUT TOTAL: {workout.total_distance(group)} {config.units.title()}, {workout_time_str}"
        
        # Simple spacing before workout total
        page_content.append(Spacer(1, 0.3*inch))
        page_content.append(Paragraph(total_text, self.styles['GrandSummary']))
        
        return page_content
    
    def _format_time_for_pdf(self, seconds: int) -> str:
        """Format seconds into MM:SS or H:MM:SS format for PDF"""
        if seconds == 0:
            return "No intervals"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"
    
    def generate_from_file(self, prac_filename: str, output_filename: str = None, title: str = None):
        """Generate PDF directly from a .prac file"""
        from parse import parse_prac
        
        # Parse the file
        config, sets = parse_prac(prac_filename)
        
        # Generate output filename if not provided
        if output_filename is None:
            base_name = os.path.splitext(prac_filename)[0]
            output_filename = f"{base_name}.pdf"
        
        # Generate the PDF - let generate_pdf handle title logic
        self.generate_pdf(config, sets, output_filename, title)
        
        return output_filename

# Command line interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pdf_generator.py <practice_file.prac> [output.pdf] [title]")
        sys.exit(1)
    
    prac_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    title = sys.argv[3] if len(sys.argv) > 3 else None
    
    # If output_file is provided but doesn't end with .pdf, add it
    if output_file and not output_file.endswith('.pdf'):
        output_file = output_file + '.pdf'
    
    try:
        generator = PDFWorkoutGenerator()
        output_path = generator.generate_from_file(prac_file, output_file, title)
        print(f"Successfully created: {output_path}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
