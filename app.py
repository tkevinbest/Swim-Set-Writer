"""
Swim Set Writer - Streamlit Web App
A web interface for creating and generating swim workout PDFs
"""

import streamlit as st
import tempfile
import os
import re
from pathlib import Path
from parse import parse_prac
from generate_pdf import PDFWorkoutGenerator

# Page configuration
st.set_page_config(
    page_title="Swim Set Writer",
    page_icon="🏊‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .example-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    /* Fix textarea tab behavior */
    .stTextArea textarea {
        tab-size: 2;
        -moz-tab-size: 2;
    }
    /* Prevent tab from moving focus */
    .stTextArea textarea:focus {
        outline: 2px solid #1f77b4;
        outline-offset: 2px;
    }
</style>

<script>
// Handle tab key in textarea to insert spaces instead of moving focus
document.addEventListener('DOMContentLoaded', function() {
    const textareas = document.querySelectorAll('.stTextArea textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('keydown', function(e) {
            if (e.key === 'Tab') {
                e.preventDefault();
                const start = this.selectionStart;
                const end = this.selectionEnd;
                const value = this.value;
                this.value = value.substring(0, start) + '  ' + value.substring(end);
                this.selectionStart = this.selectionEnd = start + 2;
            }
        });
    });
});
</script>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🏊‍♂️ Swim Set Writer</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Create well-formatted swim workout PDFs in your browser</p>', unsafe_allow_html=True)
    
    # Sidebar with examples and help
    with st.sidebar:
        st.header("📚 Examples & Help")
        
        # About section
        st.subheader("About")
        
        
        
        st.markdown("""
        **Swim Set Writer** by [@tkevinbest](https://github.com/tkevinbest)
        
        A simple tool to create well-formatted swim workout PDFs from plain text.
        
        **Features:**
        - Write workouts in .prac format
        - Multiple speed groups
        - Automatic calculations
        - Well-formatted PDF output
        """)
        
        st.markdown("---")
        
        # Documentation links
        st.subheader("📖 Documentation")
        st.markdown("""
        **Quick Reference:**
        - [📚 Full README](https://github.com/tkevinbest/Swim-Set-Writer/blob/master/README.md)
        - [📝 Full `.prac` Syntax](https://github.com/tkevinbest/Swim-Set-Writer/blob/master/SYNTAX.md)
        """)
        
        # Show full syntax in expander
        with st.expander("📖 View Complete `.prac` Syntax Reference"):
            try:
                with open("SYNTAX.md", "r", encoding="utf-8") as f:
                    full_syntax = f.read()
                st.markdown(full_syntax)
            except FileNotFoundError:
                st.error("Syntax file not found. Please check the repository.")
        
        st.markdown("---")
        
        # Quick example
        st.subheader("Quick Example")
        example_code = """title: Friday Morning Practice
units: yards
course: short

Warmup:
  200 swim @ 3:00
  200 kick @ 5:00

Main Set x3:
  4x75 rotating IM @ 1:15 [3x50 @ 1:25]
  2x50 stroke-free @ :50 [@ 1:00]

Cool Down:
  200 choice @ 4:00"""
        
        st.code(example_code, language="text")
        
        # Syntax help
        st.subheader("Syntax Help")
        
        # Read syntax from markdown file
        try:
            with open("SYNTAX.md", "r", encoding="utf-8") as f:
                syntax_content = f.read()
            
            # Extract the basic examples section
            import re
            basic_section = re.search(r'## Examples\s*\n\n### Basic Examples(.*?)(?=###|##|$)', syntax_content, re.DOTALL)
            if basic_section:
                st.markdown("**Basic Examples:**")
                st.markdown(basic_section.group(1).strip())
            
            # Show configuration section
            config_section = re.search(r'## Configuration Options(.*?)(?=##|$)', syntax_content, re.DOTALL)
            if config_section:
                st.markdown("**Configuration:**")
                st.markdown(config_section.group(1).strip())
                
        except FileNotFoundError:
            # Fallback if file doesn't exist
            st.markdown("""
            **Basic Format:**
            ```
            SET_NAME:
              [REPSx]DISTANCE DESCRIPTION [@ INTERVAL] [GROUP_VARIATION] # COMMENT
            ```
            
            **Examples:**
            - `200 swim @ 3:00` - 200 yards swim on 3:00 interval
            - `4x50 kick @ :55` - 4x50 kick on :55 interval
            - `100 swim @ 1:30 [75 swim @ 1:45]` - Group A: 100y, Group B: 75y
            - `Main Set x3:` - Repeat entire set 3 times
            """)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("✍️ Write Your Workout")
        
        # Text editor
        st.markdown("**💡 Tip:** Use 2 spaces for indentation (not tabs). Copy the example below to get started.")
        
        # Upload .prac file to populate editor
        uploaded_file = st.file_uploader(
            "Upload a .prac file",
            type=["prac", "txt"],
            accept_multiple_files=False,
            help="Load an existing practice file into the editor.",
        )
        if uploaded_file is not None:
            try:
                uploaded_text = uploaded_file.read().decode("utf-8", errors="ignore")
                st.session_state["workout_editor"] = uploaded_text
                st.success("Loaded " + uploaded_file.name + " file into the editor.")
            except Exception as e:
                st.error(f"Failed to read uploaded file: {str(e)}")
        
        workout_text = st.text_area(
            "Enter your workout in .prac format: [syntax help](https://github.com/tkevinbest/Swim-Set-Writer/blob/main/SYNTAX.md)",
            height=400,
            placeholder="title: My Practice\nunits: yards\ncourse: short\n\nWarmup:\n  200 swim @ 3:00\n\nMain Set:\n  4x100 swim @ 1:30\n\nCool Down:\n  200 easy",
            help="Write your workout using the .prac format. Use 2 spaces for indentation. See the sidebar for examples and syntax help.",
            key="workout_editor"
        )
        
        # Download current editor content as .prac
        prac_filename = "workout.prac"
        if workout_text.strip():
            try:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.prac', delete=False) as temp_prac:
                    temp_prac.write(workout_text)
                    temp_prac_path = temp_prac.name
                config_for_name, _ = parse_prac(temp_prac_path)
                os.unlink(temp_prac_path)
                if getattr(config_for_name, 'title', None):
                    clean_title = re.sub(r'[<>:"/\\|?*]', '_', config_for_name.title.strip())
                    if clean_title:
                        prac_filename = f"{clean_title}.prac"
            except Exception:
                # Fallback to default filename if parsing for name fails
                pass
        st.download_button(
            label="📥 Download .prac",
            data=workout_text.encode("utf-8"),
            file_name=prac_filename,
            mime="text/plain",
            use_container_width=True
        )
        
        # Generate PDF button
        if st.button("🏊‍♂️ Generate PDF", type="primary", use_container_width=True):
            if not workout_text.strip():
                st.error("Please enter a workout before generating the PDF.")
            else:
                try:
                    # Create temporary file
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.prac', delete=False) as temp_file:
                        temp_file.write(workout_text)
                        temp_file_path = temp_file.name
                    
                    # Parse workout to get title for filename
                    config, sets = parse_prac(temp_file_path)
                    
                    # Generate PDF
                    with st.spinner("Generating PDF..."):
                        generator = PDFWorkoutGenerator()
                        pdf_path = generator.generate_from_file(temp_file_path)
                        
                        # Read the generated PDF
                        with open(pdf_path, 'rb') as pdf_file:
                            pdf_data = pdf_file.read()
                        
                        # Clean up temporary files
                        os.unlink(temp_file_path)
                        os.unlink(pdf_path)
                    
                    # Create filename from title
                    if config.title:
                        # Clean title for filename (remove invalid characters)
                        clean_title = re.sub(r'[<>:"/\\|?*]', '_', config.title.strip())
                        filename = f"{clean_title}.pdf"
                    else:
                        filename = "swim_workout.pdf"
                    
                    # Success message and download
                    st.markdown('<div class="success-box">✅ PDF generated successfully!</div>', unsafe_allow_html=True)
                    
                    # Download button
                    st.download_button(
                        label="📥 Download PDF",
                        data=pdf_data,
                        file_name=filename,
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.error(f"Error generating PDF: {str(e)}")
                    st.code(str(e), language="text")
    
    with col2:
        st.header("📋 Preview")
        
        if workout_text.strip():
            try:
                # Parse the workout for preview
                with tempfile.NamedTemporaryFile(mode='w', suffix='.prac', delete=False) as temp_file:
                    temp_file.write(workout_text)
                    temp_file_path = temp_file.name
                
                config, sets = parse_prac(temp_file_path)
                os.unlink(temp_file_path)
                
                # Display preview
                st.subheader("Workout Summary")
                st.write(f"**Title:** {config.title or 'Untitled'}")
                st.write(f"**Units:** {config.units.title()}")
                if config.course:
                    st.write(f"**Course:** {config.course}")
                if config.author:
                    st.write(f"**Author:** {config.author}")
                
                st.subheader("Sets")
                for i, set_ in enumerate(sets, 1):
                    with st.expander(f"{i}. {set_.name}"):
                        if set_.note:
                            st.write(f"*{set_.note}*")
                        if set_.repeat > 1:
                            st.write(f"**Repeat:** {set_.repeat}x")
                        for item in set_.items:
                            st.write(f"• {item}")
                        st.write(f"**Total Distance:** {set_.total_distance()} {config.unit_symbol}")
                
                # Workout totals
                from parse import WorkoutSummary
                workout = WorkoutSummary(config, sets)
                st.subheader("Workout Totals")
                st.write(f"**Total Distance:** {workout.total_distance()} {config.unit_symbol}")
                if workout.total_time_seconds() > 0:
                    st.write(f"**Total Time:** {workout.format_time(workout.total_time_seconds())}")
                
            except Exception as e:
                st.error("Error parsing workout:")
                st.code(str(e), language="text")
        else:
            st.info("Enter a workout above to see a preview here.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**Swim Set Writer** | "
        "Created by <img src='https://github.com/tkevinbest.png' alt='GitHub Profile' style='width: 20px; height: 20px; border-radius: 50%; vertical-align: middle; margin: 0 4px;'> [@tkevinbest](https://github.com/tkevinbest) | "
        "[GitHub Repository](https://github.com/tkevinbest/Swim-Set-Writer)",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
