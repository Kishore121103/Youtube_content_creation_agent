
import streamlit as st
from workflow.enhanced_workflow import EnhancedContentWorkflow
from utils.database_manager import DatabaseManager
from utils.pdf_generator import PDFGenerator
import json
from workflow.pdf_generation_workflow import PDFGenerationWorkflow

def main():
    st.set_page_config(
        page_title="GenKodeX Content Studio",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for a more attractive UI
    st.markdown(
        """
        <style>
        .main-header {
            font-size: 3em;
            font-weight: bold;
            color: #4CAF50;
            text-align: center;
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
            font-size: 1.2em;
            font-weight: bold;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 1.1em;
            border: none;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        }
        .stButton>button:hover {
            background-color: #45a049;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.3);
        }
        .stExpander {
            border: 1px solid #ddd;
            border-radius: 8px;
            box-shadow: 1px 1px 3px rgba(0,0,0,0.1);
            margin-bottom: 10px;
        }
        .stExpander div[role="button"] p {
            font-weight: bold;
            color: #333;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.title("GenKodeX Navigation")
    
    db_manager = DatabaseManager()

    # Create tabs for different sections
    tab1, tab2 = st.tabs(["🚀 Content Generation", "📚 Content Library"])

    with tab1:
        st.markdown("<h1 class='main-header'>GenKodeX Content Studio</h1>", unsafe_allow_html=True)
        st.markdown("A robust, multi-agent system for creating high-quality educational content.")

        st.header("Generate New Content")
        topic = st.text_input("Enter your programming topic:", placeholder="e.g., Python Async/Await")

        if st.button("Generate Content", type="primary", use_container_width=True):
            if topic:
                with st.spinner("🚀 Launching the GenKodeX workflow..."):
                    try:
                        workflow = EnhancedContentWorkflow()
                        result = workflow.run(topic)
                        st.session_state.result = result
                        st.success("Content generation complete!")
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
            else:
                st.warning("Please enter a topic to begin.")
        
        if 'result' in st.session_state:
            display_results(st.session_state.result)

    with tab2:
        display_content_library(db_manager)

def display_results(result):
    st.header(f"Content for: {result['topic']}")

    # --- Metrics ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Quality Score", f"{result['quality_score']:.2f}/10")
    col2.metric("Content ID", result.get('content_id', 'N/A'))
    col3.metric("Status", "✅ Approved" if result.get('stored') else "❌ Pending")

    # --- Content Package ---
    st.subheader("Content Package")
    display_content_package(result['content_package'])

    # --- Quality Analysis ---
    st.subheader("Quality Analysis")
    display_quality_analysis(result['quality_feedback'])

    # --- Research Data ---
    st.subheader("Research Data")
    st.json(result['content_package']['research_data'])

    # --- Download PDF Button ---
    st.subheader("Download Content")
    pdf_workflow_instance = PDFGenerationWorkflow() # Initialize PDFGenerationWorkflow
    pdf_generator = PDFGenerator() # Initialize PDFGenerator

    if st.button("Download as PDF", type="secondary"):
        with st.spinner("Generating PDF..."):
            try:
                # Get structured content from LLM via workflow
                structured_content = pdf_workflow_instance.run(result['content_package'])
                
                # Generate PDF
                pdf_bytes = pdf_generator.generate_pdf(structured_content)
                
                st.download_button(
                    label="Click to Download PDF",
                    data=pdf_bytes,
                    file_name=f"{result['topic'].replace(' ', '_')}_content.pdf",
                    mime="application/pdf"
                )
                st.success("PDF generated successfully!")
            except Exception as e:
                st.error(f"Error generating PDF: {e}")

def display_content_package(content_pkg):
    with st.expander("**Titles & Metadata**", expanded=True):
        st.markdown("##### Suggested Titles")
        for title in content_pkg['titles']:
            st.markdown(f"- {title}")
        
        st.markdown("##### Description")
        st.text_area("Description", content_pkg['description'], height=150, label_visibility="collapsed")

        st.markdown("##### Hashtags")
        st.info(' '.join([f"#{tag}" for tag in content_pkg['hashtags']]))

    with st.expander("**Video Script**", expanded=True):
        st.markdown("##### Introduction")
        st.write(content_pkg['content_intro'])

        with st.expander("**Full Video Script**", expanded=False):
            full_script = content_pkg.get('youtube_content', {}).get('full_script', 'N/A')
            st.markdown(f"""
            <div style="background-color: #f0f2f6; padding: 15px; border-radius: 8px; max-height: 400px; overflow-y: auto; font-family: 'Roboto', sans-serif; line-height: 1.6;">
                {full_script}
            </div>
            """, unsafe_allow_html=True)

        with st.expander("**Brief Video Script**", expanded=False):
            brief_script = content_pkg.get('youtube_content', {}).get('brief_script', 'N/A')
            st.markdown(f"""
            <div style="background-color: #f0f2f6; padding: 15px; border-radius: 8px; max-height: 200px; overflow-y: auto; font-family: 'Roboto', sans-serif; line-height: 1.6;">
                {brief_script}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("##### Content Approaches")
        for i, approach in enumerate(content_pkg['content_approaches'].values(), 1):
            st.markdown(f"**{i}. {approach.get('title', f'Approach {i}')}**")
            explanation_text = approach.get('explanation')
            if explanation_text:
                st.write(explanation_text)
            else:
                st.write("No explanation provided.")
            if approach.get('code_examples'):
                for code in approach['code_examples']:
                    st.code(code, language='python')


def display_quality_analysis(quality_feedback):
    scores = {
        "Technical Accuracy": quality_feedback.get('technical_accuracy', 0),
        "Educational Value": quality_feedback.get('educational_value', 0),
        "Engagement Factor": quality_feedback.get('engagement_factor', 0),
        "Content Structure": quality_feedback.get('content_structure', 0),
        "SEO Optimization": quality_feedback.get('seo_optimization', 0),
    }

    for name, score in scores.items():
        # Ensure score is a float
        if isinstance(score, list):
            if score: # Take the first element if the list is not empty
                score = float(score[0])
            else: # Default to 0.0 if the list is empty
                score = 0.0
        elif not isinstance(score, (int, float)): # If it's not a list, int, or float, default to 0.0
            score = 0.0

        st.slider(name, 0.0, 10.0, score, step=0.1, disabled=True)

    st.markdown("##### Feedback")
    st.info(quality_feedback.get('feedback', 'N/A'))

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### Strengths")
        for strength in quality_feedback.get('strengths', []):
            st.success(f"- {strength}")
    with col2:
        st.markdown("##### Areas for Improvement")
        for improvement in quality_feedback.get('improvements', []):
            st.warning(f"- {improvement}")


def display_research_data(research_data):
    st.json(research_data)

def display_content_library(db_manager):
    st.markdown("<h2 style='text-align: center; color: #4CAF50;'>📚 Your Content Library</h2>", unsafe_allow_html=True)
    st.write("Browse and manage all generated content.")

    all_content = db_manager.get_all_content()

    if not all_content:
        st.info("No content found in the library. Generate some content first!")
        return

    for content in all_content:
        content_id = content['id']
        topic = content['topic']
        quality_score = content['quality_score']
        created_at = content['created_at']
        
        # Parse JSON strings back to Python objects
        try:
            titles = json.loads(content['titles'])
            description = content['description']
            hashtags = json.loads(content['hashtags'])
            content_intro = content['content_intro']
            content_approaches = json.loads(content['content_approaches'])
            research_data = json.loads(content['research_data'])
            youtube_content = json.loads(content.get('youtube_content', '{}'))
        except json.JSONDecodeError:
            st.error(f"Error decoding JSON for content ID {content_id}. Skipping display.")
            continue

        with st.expander(f"**{topic}** (Score: {quality_score:.2f}) - Created: {created_at}"):
            st.markdown("---")
            st.markdown("##### Suggested Titles")
            for title in titles:
                st.markdown(f"- {title}")
            
            st.markdown("##### Description")
            st.text_area(f"Description_{content_id}", description, height=150, label_visibility="collapsed")

            st.markdown("##### Hashtags")
            st.info(' '.join([f"#{tag}" for tag in hashtags]))

            st.markdown("##### Introduction")
            st.write(content_intro)

            with st.expander("**Full Video Script**", expanded=False):
                full_script = youtube_content.get('full_script', 'N/A')
                st.markdown(f"""
                <div style="background-color: #f0f2f6; padding: 15px; border-radius: 8px; max-height: 400px; overflow-y: auto; font-family: 'Roboto', sans-serif; line-height: 1.6;">
                    {full_script}
                </div>
                """, unsafe_allow_html=True)

            with st.expander("**Brief Video Script**", expanded=False):
                brief_script = youtube_content.get('brief_script', 'N/A')
                st.markdown(f"""
                <div style="background-color: #f0f2f6; padding: 15px; border-radius: 8px; max-height: 200px; overflow-y: auto; font-family: 'Roboto', sans-serif; line-height: 1.6;">
                    {brief_script}
                </div>
                """, unsafe_allow_html=True)

            st.markdown("##### Content Approaches")
            for i, approach in enumerate(content_approaches.values(), 1):
                st.markdown(f"**{i}. {approach.get('title', f'Approach {i}')}**")
                explanation_text = approach.get('explanation')
                if explanation_text:
                    st.write(explanation_text)
                else:
                    st.write("No explanation provided.")
                if approach.get('code_examples'):
                    for code in approach['code_examples']:
                        st.code(code, language='python')
            
            st.markdown("##### Research Data")
            st.json(research_data)

            col_dl, col_del = st.columns([0.5, 0.5])
            with col_dl:
                pdf_workflow_instance = PDFGenerationWorkflow() # Initialize PDFGenerationWorkflow
                pdf_generator = PDFGenerator() # Initialize PDFGenerator
                if st.button(f"Download PDF (ID: {content_id})", key=f"download_pdf_{content_id}", type="secondary"):
                    with st.spinner("Generating PDF..."):
                        try:
                            # Reconstruct content_package for PDF generation
                            content_package_for_pdf = {
                                'topic': topic,
                                'titles': titles,
                                'description': description,
                                'hashtags': hashtags,
                                'content_intro': content_intro,
                                'content_approaches': content_approaches,
                                'research_data': research_data
                            }
                            structured_content = pdf_workflow_instance.run(content_package_for_pdf)
                            pdf_bytes = pdf_generator.generate_pdf(structured_content)
                            
                            st.download_button(
                                label="Click to Download PDF",
                                data=pdf_bytes,
                                file_name=f"{topic.replace(' ', '_')}_ID_{content_id}.pdf",
                                mime="application/pdf",
                                key=f"final_download_{content_id}"
                            )
                            st.success("PDF generated successfully!")
                        except Exception as e:
                            st.error(f"Error generating PDF: {e}")
            with col_del:
                if st.button(f"Delete Content ID: {content_id}", key=f"delete_{content_id}", type="secondary"):
                    db_manager.delete_content(content_id)
                    st.success(f"Content ID {content_id} deleted successfully!")
                    st.rerun() # Rerun to refresh the list

if __name__ == "__main__":
    main()
