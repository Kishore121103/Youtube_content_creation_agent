from langgraph.graph import StateGraph, END
from typing import Any
from typing import Dict
from utils.llm_utils import LLMUtils
from config.settings import Config # Import Config
from concurrent.futures import ThreadPoolExecutor

class PDFGenerationWorkflow:
    def __init__(self):
        self.llm_utils = LLMUtils(provider="openrouter", model_name=Config.DEEPSEEK_MODEL, temperature=Config.TEMPERATURE, max_tokens=Config.MAX_TOKENS)
        self.workflow = self.build_workflow()

    def build_workflow(self) -> StateGraph:
        workflow = StateGraph(dict)

        workflow.add_node("generate_main_title", self.generate_main_title_node)
        workflow.add_node("generate_introduction", self.generate_introduction_node)
        workflow.add_node("generate_approaches", self.generate_approaches_node)
        workflow.add_node("generate_research_data", self.generate_research_data_node)
        workflow.add_node("generate_metadata", self.generate_metadata_node)
        workflow.add_node("assemble_pdf_content", self.assemble_pdf_content_node)

        workflow.set_entry_point("generate_main_title")

        # Parallel execution for main sections
        workflow.add_edge("generate_main_title", "generate_introduction")
        workflow.add_edge("generate_introduction", "generate_approaches")
        workflow.add_edge("generate_approaches", "generate_research_data")
        workflow.add_edge("generate_research_data", "generate_metadata")
        workflow.add_edge("generate_metadata", "assemble_pdf_content")
        workflow.add_edge("assemble_pdf_content", END)

        return workflow.compile()

    def generate_main_title_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        main_title_section = self.llm_utils._generate_main_title_section(state['content_package']['topic'])
        return {**state, "main_title_section": main_title_section}

    def generate_introduction_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        introduction_section = self.llm_utils._generate_introduction_section(state['content_package']['content_intro'])
        return {**state, "introduction_section": introduction_section}

    def generate_approaches_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        approaches_data = state['content_package']['content_approaches']
        generated_approaches = []
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            for i, (key, approach) in enumerate(approaches_data.items()):
                futures.append(executor.submit(self.llm_utils._generate_approach_section, approach, i + 1))
            for future in futures:
                generated_approaches.append(future.result())
        return {**state, "generated_approaches": generated_approaches}

    def generate_research_data_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        research_data_section = self.llm_utils._generate_research_data_section(state['content_package']['research_data'])
        return {**state, "research_data_section": research_data_section}

    def generate_metadata_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        metadata_section = self.llm_utils._generate_metadata_section(
            state['content_package']['titles'],
            state['content_package']['description'],
            state['content_package']['hashtags']
        )
        return {**state, "metadata_section": metadata_section}

    def assemble_pdf_content_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        sections = []
        sections.append(state['main_title_section'])
        sections.append(state['introduction_section'])
        sections.append({"type": "section_heading", "text": "Content Approaches", "style": {"font_size": 20, "text_color": "#36454F", "alignment": "left", "space_after": 15}})
        sections.extend(state['generated_approaches'])
        sections.extend(state['research_data_section']['content'])
        sections.extend(state['metadata_section']['content'])

        final_structured_content = {"sections": sections}
        return {**state, "final_structured_content": final_structured_content}

    def run(self, content_package: Dict[str, Any]) -> Dict[str, Any]:
        initial_state = {"content_package": content_package}
        final_state = self.workflow.invoke(initial_state)
        return final_state['final_structured_content']
