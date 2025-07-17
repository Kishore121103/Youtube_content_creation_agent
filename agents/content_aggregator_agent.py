
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ContentAggregatorAgent:
    def aggregate_content(self, titles: List[str], description_data: Dict[str, Any], 
                         content_data: Dict[str, Any]) -> Dict[str, Any]:
        logging.info("ContentAggregatorAgent: Aggregating content...")
        logging.debug(f"ContentAggregatorAgent: Titles: {titles}")
        logging.debug(f"ContentAggregatorAgent: Description Data: {description_data}")
        logging.debug(f"ContentAggregatorAgent: Content Data: {content_data}")
        
        aggregated_content = {
            'titles': titles,
            'description': description_data.get('description', ''),
            'hashtags': description_data.get('hashtags', []),
            'keywords': description_data.get('keywords', []),
            'content_intro': content_data.get('content_intro', ''),
            'content_approaches': {
                'approach_1': content_data.get('approach_1', {}),
                'approach_2': content_data.get('approach_2', {}),
                'approach_3': content_data.get('approach_3', {}),
                'approach_4': content_data.get('approach_4', {}),
                'approach_5': content_data.get('approach_5', {})
            }
        }
        logging.info("ContentAggregatorAgent: Content aggregation complete.")
        return aggregated_content
