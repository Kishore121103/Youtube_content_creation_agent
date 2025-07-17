from langgraph.graph import StateGraph, END
from agents.research_agent import ResearchAgent
from agents.title_generator_agent import TitleGeneratorAgent
from agents.description_hashtag_agent import DescriptionHashtagAgent
from agents.content_creator_agent import ContentCreatorAgent
from agents.youtube_content_agent import YouTubeContentAgent
from agents.content_aggregator_agent import ContentAggregatorAgent
from agents.quality_assurance_agent import QualityAssuranceAgent
from utils.database_manager import DatabaseManager
from typing import TypedDict, List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the state for the graph
class ContentGenerationState(TypedDict):
    topic: str
    research_data: Dict[str, Any]
    titles: List[str]
    description: str
    hashtags: List[str]
    content_intro: str
    content_approaches: Dict[str, Any]
    youtube_content: Dict[str, str]
    content_package: Dict[str, Any]
    quality_feedback: Dict[str, Any]
    quality_score: float
    stored: bool
    content_id: int
    iteration: int

class EnhancedContentWorkflow:
    def __init__(self):
        logging.info("EnhancedContentWorkflow: Initializing workflow.")
        self.workflow = StateGraph(ContentGenerationState)
        self._build_graph()
        self.app = self.workflow.compile()
        self.db_manager = DatabaseManager()
        logging.info("EnhancedContentWorkflow: Workflow initialized and compiled.")

    def _build_graph(self):
        logging.info("EnhancedContentWorkflow: Building graph nodes and edges.")
        # 1. Define the nodes (agents)
        self.workflow.add_node("research", self.run_research_agent)
        self.workflow.add_node("orchestrate_parallel_generation", self.orchestrate_parallel_generation_node)
        self.workflow.add_node("aggregate_content", self.run_content_aggregator_agent)
        self.workflow.add_node("quality_assurance", self.run_quality_assurance_agent)
        self.workflow.add_node("store_content", self.store_content_in_db)
        logging.info("EnhancedContentWorkflow: Nodes added.")

        # 2. Define the edges (flow)
        self.workflow.set_entry_point("research")
        self.workflow.add_edge("research", "orchestrate_parallel_generation")
        self.workflow.add_edge("orchestrate_parallel_generation", "aggregate_content")
        self.workflow.add_edge("aggregate_content", "quality_assurance")
        self.workflow.add_conditional_edges(
            "quality_assurance",
            self.quality_decision,
            {
                "approve": "store_content",
                "refine": "orchestrate_parallel_generation"
            }
        )
        self.workflow.add_edge("store_content", END)
        logging.info("EnhancedContentWorkflow: Edges defined, including quality assurance loop.")

    # --- Agent Execution Methods ---

    def run_research_agent(self, state):
        logging.info("--- Running Research Agent ---")
        topic = state['topic']
        agent = ResearchAgent()
        research_data = agent.conduct_research(topic)
        logging.debug(f"Research Agent: Research data generated: {research_data.keys()}")
        return {"research_data": research_data}

    def orchestrate_parallel_generation_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Orchestrate parallel generation of YouTube content, intro, approaches, and metadata."""
        logging.info("--- Orchestrating Parallel Content Generation ---")
        topic = state['topic']
        research_data = state['research_data']
        iteration = state.get('iteration', 1)
        logging.info(f"Orchestrator: Current iteration: {iteration}")

        # Initialize agents
        title_agent = TitleGeneratorAgent()
        desc_agent = DescriptionHashtagAgent()
        content_creator = ContentCreatorAgent()
        youtube_agent = YouTubeContentAgent()

        # Define the different pedagogical approaches for content generation
        approach_types = {
            "approach_1": "The Absolute Beginner's Way",
            "approach_2": "The Intermediate Level",
            "approach_3": "The Advanced Technique",
            "approach_4": "The Professional/Real-World Implementation",
            "approach_5": "The Expert's Insight/Common Pitfall"
        }

        with ThreadPoolExecutor(max_workers=8) as executor:
            logging.info("Orchestrator: Submitting parallel content generation tasks.")
            # --- Submit all tasks to the executor ---
            
            # Submit metadata generation tasks
            title_future = executor.submit(title_agent.generate_titles, topic, research_data)
            desc_future = executor.submit(desc_agent.generate_description_and_hashtags, topic, research_data)
            
            # Submit content generation tasks
            intro_future = executor.submit(content_creator.create_content_introduction, topic, research_data)
            approach_futures = {
                key: executor.submit(content_creator.generate_single_approach, topic, research_data, desc)
                for key, desc in approach_types.items()
            }

            # --- Retrieve results from futures ---
            logging.info("Orchestrator: Retrieving results from parallel tasks.")
            # Retrieve metadata
            titles = title_future.result()
            desc_hashtags = desc_future.result()
            
            # Retrieve core content
            content_intro = intro_future.result()
            content_approaches = {key: future.result() for key, future in approach_futures.items()}

            # --- Generate YouTube scripts based on the generated content ---
            
            # This task depends on the intro and approaches, so it runs after they are complete.
            # We can submit it to the same executor.
            youtube_future = executor.submit(
                youtube_agent.generate_video_content, 
                topic, 
                research_data
            )
            youtube_content = youtube_future.result()

        # --- Package the results ---
        logging.info("Orchestrator: Packaging generated content.")
        return {
            "titles": titles,
            "description": desc_hashtags.get('description', ''),
            "hashtags": desc_hashtags.get('hashtags', []),
            "content_intro": content_intro,
            "content_approaches": content_approaches,
            "youtube_content": youtube_content,
            "iteration": iteration  # Carry over the iteration count
        }

    def run_content_aggregator_agent(self, state):
        logging.info("--- Running Content Aggregator Agent ---")
        agent = ContentAggregatorAgent()
        description_data = {
            'description': state['description'],
            'hashtags': state['hashtags']
        }
        content_data = {
            'content_intro': state['content_intro'],
            'approach_1': state['content_approaches'].get('approach_1', {}),
            'approach_2': state['content_approaches'].get('approach_2', {}),
            'approach_3': state['content_approaches'].get('approach_3', {}),
            'approach_4': state['content_approaches'].get('approach_4', {}),
            'approach_5': state['content_approaches'].get('approach_5', {}),
            'youtube_content': state['youtube_content']
        }
        content_package = agent.aggregate_content(
            titles=state['titles'],
            description_data=description_data,
            content_data=content_data
        )
        logging.debug(f"Content Aggregator Agent: Aggregated content package keys: {content_package.keys()}")
        return {"content_package": content_package}

    def run_quality_assurance_agent(self, state):
        logging.info("--- Running Quality Assurance Agent ---")
        content_package = state['content_package']
        agent = QualityAssuranceAgent()
        quality_feedback = agent.evaluate_content(content_package)
        
        average_score = quality_feedback.get('overall_score', 0.0)
        logging.info(f"Quality Assurance Agent: Content evaluated with overall score: {average_score:.2f}")
        logging.debug(f"Quality Assurance Agent: Quality feedback: {quality_feedback}")
        
        return {"quality_feedback": quality_feedback, "quality_score": average_score}

    def quality_decision(self, state: Dict[str, Any]) -> str:
        """Determine if the content quality is sufficient."""
        iteration = state.get('iteration', 1)
        quality_score = state.get('quality_score', 0)
        logging.info(f"Quality Decision: Current iteration: {iteration}, Quality Score: {quality_score:.2f}")
        
        if quality_score >= 7.5 or iteration >= 2:
            logging.info(f"Content for '{state['topic']}' approved with score {quality_score:.2f}.")
            return "approve"
        else:
            logging.info(f"Content quality score is {quality_score:.2f}. Refining content, iteration {iteration + 1}.")
            state['iteration'] = iteration + 1
            return "refine"

    def store_content_in_db(self, state):
        logging.info("--- Storing Content in Database ---")
        content_package = state['content_package']
        content_data_to_save = {
            'topic': state['topic'],
            'titles': content_package.get('titles', []),
            'description': content_package.get('description', ''),
            'hashtags': content_package.get('hashtags', []),
            'content_intro': content_package.get('content_intro', ''),
            'content_approaches': content_package.get('content_approaches', {}),
            'quality_score': state.get('quality_score', 0.0),
            'research_data': state.get('research_data', {}),
            'youtube_content': content_package.get('youtube_content', {'full_script': '', 'brief_script': ''}),
            'approved': False, # Default value, can be updated later
            'approval_status': 'pending' # Default value, can be updated later
        }
        content_id = self.db_manager.save_content(content_data_to_save)
        logging.info(f"Content stored in DB with ID: {content_id}")
        state['stored'] = True
        state['content_id'] = content_id
        return state

    def run(self, topic: str):
        """
        Executes the entire content generation workflow.
        """
        logging.info(f"EnhancedContentWorkflow: Starting run for topic: {topic}")
        initial_state = {"topic": topic, "iteration": 1}
        final_state = initial_state
        for s in self.app.stream(initial_state):
            # LangGraph stream yields updates, so merge them into final_state
            for key, value in s.items():
                final_state[key] = value
            logging.debug(f"EnhancedContentWorkflow: Current state after node execution: {list(s.keys())[0]}")

        if final_state:
            logging.info(f"EnhancedContentWorkflow: Workflow finished. Final state: {final_state.keys()}")
            # Return a comprehensive result for app.py
            return {
                "topic": final_state["topic"],
                "content_package": final_state.get("aggregate_content", {}).get("content_package", {}),
                "quality_score": final_state.get("quality_score", 0.0),
                "quality_feedback": final_state.get("quality_feedback", {}),
                "content_id": final_state.get("content_id", None)
            }
        logging.warning("EnhancedContentWorkflow: Workflow finished without a final state.")
        return {}
