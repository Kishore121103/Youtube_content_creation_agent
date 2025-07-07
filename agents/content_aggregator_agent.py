
from typing import Dict, Any, List

class ContentAggregatorAgent:
    def aggregate_content(self, titles: List[str], description_data: Dict[str, Any], 
                         content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Combine all content components into final package"""
        return {
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
