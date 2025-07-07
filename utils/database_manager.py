
import sqlite3
import json
from typing import Dict, Any, List
from config.settings import Config

class DatabaseManager:
    def __init__(self):
        self.db_path = Config.DATABASE_PATH
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Content table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                titles TEXT NOT NULL,
                description TEXT NOT NULL,
                hashtags TEXT NOT NULL,
                content_intro TEXT NOT NULL,
                content_approaches TEXT NOT NULL,
                quality_score REAL NOT NULL,
                research_data TEXT,
                full_script TEXT,
                brief_script TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                approved BOOLEAN DEFAULT FALSE,
                approval_status TEXT DEFAULT 'pending'
            )
        ''')
        
        # Research cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS research_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                research_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Content patterns table for context
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_category TEXT NOT NULL,
                successful_patterns TEXT NOT NULL,
                common_structures TEXT NOT NULL,
                effective_intros TEXT NOT NULL,
                audience_preferences TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_content(self, content_data: Dict[str, Any]) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO content (topic, titles, description, hashtags, content_intro, 
                               content_approaches, quality_score, research_data, full_script, brief_script, approved, approval_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            content_data['topic'],
            json.dumps(content_data['titles']),
            content_data['description'],
            json.dumps(content_data['hashtags']),
            content_data['content_intro'],
            json.dumps(content_data['content_approaches']),
            content_data['quality_score'],
            json.dumps(content_data.get('research_data', {})),
            content_data['youtube_content']['full_script'],
            content_data['youtube_content']['brief_script'],
            content_data.get('approved', False),
            content_data.get('approval_status', 'pending')
        ))
        
        content_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return content_id
    
    def get_approved_content(self, limit: int = 10) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM content WHERE approved = TRUE 
            ORDER BY created_at DESC LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    
    def get_pending_content(self, limit: int = 10) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM content WHERE approval_status = 'pending' 
            ORDER BY created_at DESC LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    
    def update_approval_status(self, content_id: int, approved: bool, status: str = None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if status is None:
            status = 'approved' if approved else 'rejected'
        
        cursor.execute('''
            UPDATE content 
            SET approved = ?, approval_status = ? 
            WHERE id = ?
        ''', (approved, status, content_id))
        
        conn.commit()
        conn.close()
    
    def delete_content(self, content_id: int):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM content WHERE id = ?", (content_id,))
        conn.commit()
        conn.close()

    def get_all_content(self) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM content ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    def get_content_context(self, topic: str, limit: int = 5) -> Dict[str, Any]:
        """Get context from similar approved content"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get similar approved content
        cursor.execute('''
            SELECT topic, content_intro, content_approaches, quality_score, hashtags
            FROM content 
            WHERE approved = TRUE 
            AND (topic LIKE ? OR topic LIKE ? OR topic LIKE ?)
            ORDER BY quality_score DESC, created_at DESC 
            LIMIT ?
        ''', (f'%{topic}%', f'%{topic.split()[0]}%', f'%{topic.split()[-1]}%', limit))
        
        similar_content = cursor.fetchall()
        
        # Get overall successful patterns
        cursor.execute('''
            SELECT content_intro, content_approaches, hashtags, quality_score
            FROM content 
            WHERE approved = TRUE AND quality_score >= 8.0
            ORDER BY quality_score DESC
            LIMIT ?
        ''', (limit,))
        
        high_quality_content = cursor.fetchall()
        
        conn.close()
        
        return {
            'similar_content': similar_content,
            'high_quality_patterns': high_quality_content,
            'topic_keywords': topic.split(),
            'context_available': len(similar_content) > 0 or len(high_quality_content) > 0
        }
