"""
Database module for Afaan Oromo LLM System
Handles conversation persistence and analytics using SQLite
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from contextlib import contextmanager


class Database:
    """SQLite database manager for conversation storage and analytics."""
    
    def __init__(self, db_path: str = "conversations.db"):
        """Initialize database connection and create tables if needed."""
        self.db_path = db_path
        self._init_database()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _init_database(self):
        """Create database tables if they don't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_updated TEXT NOT NULL,
                    message_count INTEGER DEFAULT 0
                )
            """)
            
            # Messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    token_count INTEGER DEFAULT 0,
                    FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
                )
            """)
            
            # Analytics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    query_type TEXT,
                    response_time REAL,
                    error TEXT,
                    timestamp TEXT NOT NULL,
                    input_length INTEGER,
                    output_length INTEGER,
                    FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE SET NULL
                )
            """)
            
            # Create indexes for better query performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_session 
                ON messages(session_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_analytics_timestamp 
                ON analytics(timestamp)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_updated 
                ON sessions(last_updated)
            """)
    
    # ==================== Session Management ====================
    
    def create_session(self, session_id: str, title: str) -> Dict[str, Any]:
        """
        Create a new conversation session.
        
        Args:
            session_id: Unique identifier for the session
            title: Display title for the session
            
        Returns:
            Dictionary with session information
        """
        now = datetime.now().isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sessions (id, title, created_at, last_updated, message_count)
                VALUES (?, ?, ?, ?, 0)
            """, (session_id, title, now, now))
        
        return {
            'id': session_id,
            'title': title,
            'created_at': now,
            'last_updated': now,
            'message_count': 0
        }
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, created_at, last_updated, message_count
                FROM sessions
                WHERE id = ?
            """, (session_id,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def list_sessions(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List all sessions ordered by last update.
        
        Args:
            limit: Maximum number of sessions to return
            offset: Number of sessions to skip
            
        Returns:
            List of session dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, created_at, last_updated, message_count
                FROM sessions
                ORDER BY last_updated DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def update_session(self, session_id: str, title: Optional[str] = None):
        """Update session information."""
        now = datetime.now().isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if title:
                cursor.execute("""
                    UPDATE sessions
                    SET title = ?, last_updated = ?
                    WHERE id = ?
                """, (title, now, session_id))
            else:
                cursor.execute("""
                    UPDATE sessions
                    SET last_updated = ?
                    WHERE id = ?
                """, (now, session_id))
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session and all its messages.
        
        Returns:
            True if session was deleted, False if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            return cursor.rowcount > 0
    
    # ==================== Message Management ====================
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        token_count: int = 0
    ) -> int:
        """
        Add a message to a session.
        
        Args:
            session_id: ID of the session
            role: 'user' or 'model'
            content: Message content
            token_count: Estimated token count
            
        Returns:
            Message ID
        """
        now = datetime.now().isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Insert message
            cursor.execute("""
                INSERT INTO messages (session_id, role, content, timestamp, token_count)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, role, content, now, token_count))
            
            message_id = cursor.lastrowid
            
            # Update session message count and last_updated
            cursor.execute("""
                UPDATE sessions
                SET message_count = message_count + 1,
                    last_updated = ?
                WHERE id = ?
            """, (now, session_id))
        
        return message_id
    
    def get_messages(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all messages for a session.
        
        Args:
            session_id: ID of the session
            limit: Optional limit on number of messages to return
            
        Returns:
            List of message dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if limit:
                cursor.execute("""
                    SELECT id, session_id, role, content, timestamp, token_count
                    FROM messages
                    WHERE session_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (session_id, limit))
            else:
                cursor.execute("""
                    SELECT id, session_id, role, content, timestamp, token_count
                    FROM messages
                    WHERE session_id = ?
                    ORDER BY timestamp ASC
                """, (session_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get conversation history formatted for LLM API.
        
        Returns:
            List of messages in format: [{"role": "user", "parts": ["text"]}, ...]
        """
        messages = self.get_messages(session_id)
        return [
            {
                "role": msg["role"],
                "parts": [msg["content"]]
            }
            for msg in messages
        ]
    
    # ==================== Analytics ====================
    
    def log_analytics(
        self,
        session_id: Optional[str] = None,
        query_type: Optional[str] = None,
        response_time: Optional[float] = None,
        error: Optional[str] = None,
        input_length: int = 0,
        output_length: int = 0
    ):
        """Log analytics data for a query."""
        now = datetime.now().isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO analytics 
                (session_id, query_type, response_time, error, timestamp, input_length, output_length)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (session_id, query_type, response_time, error, now, input_length, output_length))
    
    def get_analytics_summary(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get analytics summary.
        
        Args:
            start_date: ISO format date string
            end_date: ISO format date string
            
        Returns:
            Dictionary with analytics summary
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Build query with optional date filters
            query = """
                SELECT 
                    COUNT(*) as total_queries,
                    COUNT(CASE WHEN error IS NOT NULL THEN 1 END) as error_count,
                    AVG(response_time) as avg_response_time,
                    AVG(input_length) as avg_input_length,
                    AVG(output_length) as avg_output_length,
                    MIN(timestamp) as first_query,
                    MAX(timestamp) as last_query
                FROM analytics
                WHERE 1=1
            """
            params = []
            
            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date)
            
            cursor.execute(query, params)
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return {}
    
    def get_error_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent error logs."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, session_id, query_type, error, timestamp
                FROM analytics
                WHERE error IS NOT NULL
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    # ==================== Utility Methods ====================
    
    def get_total_sessions(self) -> int:
        """Get total number of sessions."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM sessions")
            return cursor.fetchone()['count']
    
    def get_total_messages(self) -> int:
        """Get total number of messages."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM messages")
            return cursor.fetchone()['count']
    
    def cleanup_old_sessions(self, days: int = 30) -> int:
        """
        Delete sessions older than specified days.
        
        Returns:
            Number of sessions deleted
        """
        cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
        cutoff_str = cutoff_date.isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM sessions
                WHERE last_updated < ?
            """, (cutoff_str,))
            
            return cursor.rowcount


# Singleton instance
_db_instance = None


def get_database(db_path: str = "conversations.db") -> Database:
    """Get or create database singleton instance."""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(db_path)
    return _db_instance

