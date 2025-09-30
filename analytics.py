import sqlite3
import json
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
from typing import Dict, List, Any, Optional
import logging
import hashlib
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = "data/algebra_visualizer.db"):
        self.db_path = db_path
        self._init_database()
    
    def _get_connection(self):
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_database(self):
        """Initialize all database tables"""
        try:
            conn = self._get_connection()
            c = conn.cursor()
            
            # Users table (extended from auth system)
            c.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    role TEXT DEFAULT 'student',
                    is_verified INTEGER DEFAULT 0,
                    verification_token TEXT,
                    reset_token TEXT,
                    reset_token_expiry TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    profile_data TEXT DEFAULT '{}',
                    preferences TEXT DEFAULT '{}',
                    subscription_level TEXT DEFAULT 'free',
                    timezone TEXT DEFAULT 'UTC'
                )
            ''')
            
            # User progress and gamification
            c.execute('''
                CREATE TABLE IF NOT EXISTS user_progress (
                    user_id INTEGER PRIMARY KEY,
                    total_points INTEGER DEFAULT 0,
                    current_level INTEGER DEFAULT 1,
                    problems_attempted INTEGER DEFAULT 0,
                    problems_solved INTEGER DEFAULT 0,
                    streak_days INTEGER DEFAULT 0,
                    last_active DATE,
                    total_study_time INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Concept mastery
            c.execute('''
                CREATE TABLE IF NOT EXISTS concept_mastery (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    concept TEXT NOT NULL,
                    proficiency REAL DEFAULT 0,
                    problems_attempted INTEGER DEFAULT 0,
                    problems_solved INTEGER DEFAULT 0,
                    last_practiced TIMESTAMP,
                    confidence_score REAL DEFAULT 0,
                    mastery_level TEXT DEFAULT 'beginner',
                    UNIQUE(user_id, concept),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Achievements
            c.execute('''
                CREATE TABLE IF NOT EXISTS achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    achievement_id TEXT NOT NULL,
                    achievement_name TEXT NOT NULL,
                    achievement_description TEXT,
                    points_awarded INTEGER DEFAULT 0,
                    achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Problem history
            c.execute('''
                CREATE TABLE IF NOT EXISTS problem_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    problem_type TEXT NOT NULL,
                    problem_text TEXT NOT NULL,
                    user_solution TEXT,
                    correct_solution TEXT,
                    is_correct INTEGER DEFAULT 0,
                    time_taken INTEGER DEFAULT 0,
                    difficulty TEXT DEFAULT 'medium',
                    concepts_involved TEXT DEFAULT '[]',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Study sessions
            c.execute('''
                CREATE TABLE IF NOT EXISTS study_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    session_type TEXT NOT NULL,
                    duration INTEGER DEFAULT 0,
                    concepts_covered TEXT DEFAULT '[]',
                    problems_solved INTEGER DEFAULT 0,
                    accuracy REAL DEFAULT 0,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    notes TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Math formulas and content
            c.execute('''
                CREATE TABLE IF NOT EXISTS math_formulas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    formula_name TEXT NOT NULL,
                    formula_latex TEXT NOT NULL,
                    category TEXT NOT NULL,
                    difficulty TEXT DEFAULT 'beginner',
                    description TEXT,
                    example_usage TEXT,
                    visualization_type TEXT,
                    tags TEXT DEFAULT '[]',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # User favorites
            c.execute('''
                CREATE TABLE IF NOT EXISTS user_favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    item_type TEXT NOT NULL,
                    item_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, item_type, item_id),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Notifications
            c.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    notification_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    is_read INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    action_url TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Analytics events
            c.execute('''
                CREATE TABLE IF NOT EXISTS analytics_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    event_type TEXT NOT NULL,
                    event_data TEXT DEFAULT '{}',
                    ip_address TEXT,
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            c.execute('CREATE INDEX IF NOT EXISTS idx_user_progress_user_id ON user_progress(user_id)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_concept_mastery_user_id ON concept_mastery(user_id)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_problem_history_user_id ON problem_history(user_id)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_problem_history_created_at ON problem_history(created_at)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_study_sessions_user_id ON study_sessions(user_id)')
            
            conn.commit()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
        finally:
            conn.close()
    
    # User Management Methods
    def create_user(self, username: str, email: str, password_hash: str, salt: str, **kwargs) -> bool:
        """Create a new user with extended profile"""
        try:
            conn = self._get_connection()
            c = conn.cursor()
            
            profile_data = kwargs.get('profile_data', {})
            preferences = kwargs.get('preferences', {})
            role = kwargs.get('role', 'student')
            
            c.execute('''
                INSERT INTO users (username, email, password_hash, salt, role, profile_data, preferences)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, email, password_hash, salt, role, json.dumps(profile_data), json.dumps(preferences)))
            
            user_id = c.lastrowid
            
            # Initialize user progress
            c.execute('''
                INSERT INTO user_progress (user_id) VALUES (?)
            ''', (user_id,))
            
            conn.commit()
            logger.info(f"User created successfully: {username}")
            return True
            
        except sqlite3.IntegrityError:
            logger.warning(f"User already exists: {username}")
            return False
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False
        finally:
            conn.close()
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username with full profile"""
        try:
            conn = self._get_connection()
            c = conn.cursor()
            
            c.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = c.fetchone()
            
            if user:
                return dict(user)
            return None
            
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
        finally:
            conn.close()
    
    def update_user_profile(self, user_id: int, profile_data: Dict) -> bool:
        """Update user profile data"""
        try:
            conn = self._get_connection()
            c = conn.cursor()
            
            c.execute('''
                UPDATE users SET profile_data = ? WHERE id = ?
            ''', (json.dumps(profile_data), user_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            return False
        finally:
            conn.close()
    
    # Progress Tracking Methods
    def update_user_progress(self, user_id: int, problem_data: Dict) -> bool:
        """Update user progress after problem attempt"""
        try:
            conn = self._get_connection()
            c = conn.cursor()
            
            # Update problem history
            c.execute('''
                INSERT INTO problem_history 
                (user_id, problem_type, problem_text, user_solution, correct_solution, 
                 is_correct, time_taken, difficulty, concepts_involved)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                problem_data.get('problem_type', 'unknown'),
                problem_data.get('problem_text', ''),
                problem_data.get('user_solution', ''),
                problem_data.get('correct_solution', ''),
                problem_data.get('is_correct', 0),
                problem_data.get('time_taken', 0),
                problem_data.get('difficulty', 'medium'),
                json.dumps(problem_data.get('concepts_involved', []))
            ))
            
            # Update concept mastery
            concepts = problem_data.get('concepts_involved', [])
            for concept in concepts:
                self._update_concept_mastery(c, user_id, concept, problem_data.get('is_correct', 0))
            
            # Update user progress stats
            self._update_user_stats(c, user_id, problem_data.get('is_correct', 0))
            
            conn.commit()
            logger.info(f"Progress updated for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating progress: {e}")
            return False
        finally:
            conn.close()
    
    def _update_concept_mastery(self, cursor, user_id: int, concept: str, is_correct: bool):
        """Update concept mastery for a user"""
        # Get current mastery
        cursor.execute('''
            SELECT proficiency, problems_attempted, problems_solved 
            FROM concept_mastery WHERE user_id = ? AND concept = ?
        ''', (user_id, concept))
        
        result = cursor.fetchone()
        
        if result:
            proficiency, attempted, solved = result
            new_attempted = attempted + 1
            new_solved = solved + (1 if is_correct else 0)
            
            # Calculate new proficiency (weighted average)
            new_proficiency = (proficiency * attempted + (100 if is_correct else 0)) / new_attempted
            
            cursor.execute('''
                UPDATE concept_mastery 
                SET proficiency = ?, problems_attempted = ?, problems_solved = ?, 
                    last_practiced = CURRENT_TIMESTAMP
                WHERE user_id = ? AND concept = ?
            ''', (new_proficiency, new_attempted, new_solved, user_id, concept))
        else:
            # First time practicing this concept
            proficiency = 100 if is_correct else 0
            cursor.execute('''
                INSERT INTO concept_mastery 
                (user_id, concept, proficiency, problems_attempted, problems_solved, last_practiced)
                VALUES (?, ?, ?, 1, ?, CURRENT_TIMESTAMP)
            ''', (user_id, concept, proficiency, 1 if is_correct else 0))
    
    def _update_user_stats(self, cursor, user_id: int, is_correct: bool):
        """Update user statistics"""
        cursor.execute('''
            UPDATE user_progress 
            SET problems_attempted = problems_attempted + 1,
                problems_solved = problems_solved + ?,
                last_active = CURRENT_DATE,
                total_points = total_points + ?
            WHERE user_id = ?
        ''', (1 if is_correct else 0, 10 if is_correct else 1, user_id))
        
        # Update streak
        cursor.execute('SELECT last_active FROM user_progress WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if result and result[0]:
            last_active = datetime.strptime(result[0], '%Y-%m-%d').date()
            today = datetime.now().date()
            
            if today == last_active:
                # Already updated today
                pass
            elif today - last_active == timedelta(days=1):
                # Consecutive day
                cursor.execute('''
                    UPDATE user_progress SET streak_days = streak_days + 1 WHERE user_id = ?
                ''', (user_id,))
            else:
                # Broken streak
                cursor.execute('''
                    UPDATE user_progress SET streak_days = 1 WHERE user_id = ?
                ''', (user_id,))
    
    # Analytics and Reporting Methods
    def get_user_progress_report(self, user_id: int) -> Dict:
        """Get comprehensive progress report for a user"""
        try:
            conn = self._get_connection()
            
            # Basic progress
            progress_df = pd.read_sql('''
                SELECT * FROM user_progress WHERE user_id = ?
            ''', conn, params=(user_id,))
            
            # Concept mastery
            concepts_df = pd.read_sql('''
                SELECT concept, proficiency, problems_attempted, problems_solved, mastery_level
                FROM concept_mastery WHERE user_id = ? ORDER BY proficiency DESC
            ''', conn, params=(user_id,))
            
            # Recent activity
            recent_activity_df = pd.read_sql('''
                SELECT problem_type, is_correct, time_taken, created_at
                FROM problem_history 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT 50
            ''', conn, params=(user_id,))
            
            # Study time analysis
            study_time_df = pd.read_sql('''
                SELECT DATE(start_time) as study_date, 
                       SUM(duration) as total_study_time,
                       COUNT(*) as sessions_count
                FROM study_sessions 
                WHERE user_id = ? 
                GROUP BY DATE(start_time)
                ORDER BY study_date DESC
                LIMIT 30
            ''', conn, params=(user_id,))
            
            conn.close()
            
            return {
                'basic_progress': progress_df.to_dict('records')[0] if not progress_df.empty else {},
                'concept_mastery': concepts_df.to_dict('records'),
                'recent_activity': recent_activity_df.to_dict('records'),
                'study_analytics': study_time_df.to_dict('records'),
                'summary': self._generate_progress_summary(progress_df, concepts_df)
            }
            
        except Exception as e:
            logger.error(f"Error generating progress report: {e}")
            return {}
    
    def _generate_progress_summary(self, progress_df, concepts_df) -> Dict:
        """Generate summary statistics from progress data"""
        if progress_df.empty or concepts_df.empty:
            return {}
        
        progress = progress_df.iloc[0]
        total_concepts = len(concepts_df)
        mastered_concepts = len(concepts_df[concepts_df['proficiency'] >= 80])
        
        return {
            'total_study_time_minutes': progress.get('total_study_time', 0),
            'accuracy_rate': (progress['problems_solved'] / progress['problems_attempted'] * 100) if progress['problems_attempted'] > 0 else 0,
            'mastered_concepts': mastered_concepts,
            'total_concepts': total_concepts,
            'current_streak': progress.get('streak_days', 0),
            'average_time_per_problem': self._calculate_average_time(progress_df)
        }
    
    def _calculate_average_time(self, progress_df) -> float:
        """Calculate average time per problem"""
        # This would typically query problem_history for actual times
        return 45.0  # Placeholder
    
    # Study Session Management
    def start_study_session(self, user_id: int, session_type: str = "practice") -> int:
        """Start a new study session and return session ID"""
        try:
            conn = self._get_connection()
            c = conn.cursor()
            
            c.execute('''
                INSERT INTO study_sessions (user_id, session_type, start_time)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, session_type))
            
            session_id = c.lastrowid
            conn.commit()
            conn.close()
            
            return session_id
            
        except Exception as e:
            logger.error(f"Error starting study session: {e}")
            return -1
    
    def end_study_session(self, session_id: int, concepts_covered: List[str] = None, 
                         problems_solved: int = 0, accuracy: float = 0, notes: str = ""):
        """End a study session and update statistics"""
        try:
            conn = self._get_connection()
            c = conn.cursor()
            
            # Calculate duration
            c.execute('SELECT start_time FROM study_sessions WHERE id = ?', (session_id,))
            result = c.fetchone()
            
            if result:
                start_time = datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S')
                duration = int((datetime.now() - start_time).total_seconds() / 60)  # in minutes
                
                c.execute('''
                    UPDATE study_sessions 
                    SET duration = ?, concepts_covered = ?, problems_solved = ?, 
                        accuracy = ?, end_time = CURRENT_TIMESTAMP, notes = ?
                    WHERE id = ?
                ''', (duration, json.dumps(concepts_covered or []), problems_solved, 
                     accuracy, notes, session_id))
                
                # Update total study time
                c.execute('''
                    UPDATE user_progress 
                    SET total_study_time = total_study_time + ? 
                    WHERE user_id = (SELECT user_id FROM study_sessions WHERE id = ?)
                ''', (duration, session_id))
                
                conn.commit()
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Error ending study session: {e}")
    
    # Formula and Content Management
    def get_formulas_by_category(self, category: str = None, difficulty: str = None) -> List[Dict]:
        """Get math formulas with filtering"""
        try:
            conn = self._get_connection()
            
            query = "SELECT * FROM math_formulas WHERE 1=1"
            params = []
            
            if category:
                query += " AND category = ?"
                params.append(category)
            
            if difficulty:
                query += " AND difficulty = ?"
                params.append(difficulty)
            
            query += " ORDER BY category, formula_name"
            
            formulas_df = pd.read_sql(query, conn, params=params)
            conn.close()
            
            return formulas_df.to_dict('records')
            
        except Exception as e:
            logger.error(f"Error getting formulas: {e}")
            return []
    
    def add_formula(self, formula_data: Dict) -> bool:
        """Add a new math formula to the database"""
        try:
            conn = self._get_connection()
            c = conn.cursor()
            
            c.execute('''
                INSERT INTO math_formulas 
                (formula_name, formula_latex, category, difficulty, description, example_usage, visualization_type, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                formula_data['formula_name'],
                formula_data['formula_latex'],
                formula_data['category'],
                formula_data.get('difficulty', 'beginner'),
                formula_data.get('description', ''),
                formula_data.get('example_usage', ''),
                formula_data.get('visualization_type', 'graph'),
                json.dumps(formula_data.get('tags', []))
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error adding formula: {e}")
            return False
    
    # Favorites Management
    def add_to_favorites(self, user_id: int, item_type: str, item_id: int) -> bool:
        """Add item to user favorites"""
        try:
            conn = self._get_connection()
            c = conn.cursor()
            
            c.execute('''
                INSERT OR IGNORE INTO user_favorites (user_id, item_type, item_id)
                VALUES (?, ?, ?)
            ''', (user_id, item_type, item_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error adding to favorites: {e}")
            return False
    
    def get_user_favorites(self, user_id: int, item_type: str = None) -> List[Dict]:
        """Get user's favorite items"""
        try:
            conn = self._get_connection()
            
            query = "SELECT * FROM user_favorites WHERE user_id = ?"
            params = [user_id]
            
            if item_type:
                query += " AND item_type = ?"
                params.append(item_type)
            
            favorites_df = pd.read_sql(query, conn, params=params)
            conn.close()
            
            return favorites_df.to_dict('records')
            
        except Exception as e:
            logger.error(f"Error getting favorites: {e}")
            return []
    
    # Notifications System
    def create_notification(self, user_id: int, notification_type: str, title: str, 
                          message: str, action_url: str = None, expires_in_hours: int = 24):
        """Create a new notification for user"""
        try:
            conn = self._get_connection()
            c = conn.cursor()
            
            expires_at = datetime.now() + timedelta(hours=expires_in_hours)
            
            c.execute('''
                INSERT INTO notifications 
                (user_id, notification_type, title, message, action_url, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, notification_type, title, message, action_url, expires_at))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            return False
    
    def get_unread_notifications(self, user_id: int) -> List[Dict]:
        """Get user's unread notifications"""
        try:
            conn = self._get_connection()
            
            notifications_df = pd.read_sql('''
                SELECT * FROM notifications 
                WHERE user_id = ? AND is_read = 0 AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
                ORDER BY created_at DESC
                LIMIT 20
            ''', conn, params=(user_id,))
            
            conn.close()
            return notifications_df.to_dict('records')
            
        except Exception as e:
            logger.error(f"Error getting notifications: {e}")
            return []
    
    # Analytics and Insights
    def log_analytics_event(self, user_id: int, event_type: str, event_data: Dict = None):
        """Log analytics event"""
        try:
            conn = self._get_connection()
            c = conn.cursor()
            
            c.execute('''
                INSERT INTO analytics_events (user_id, event_type, event_data)
                VALUES (?, ?, ?)
            ''', (user_id, event_type, json.dumps(event_data or {})))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error logging analytics event: {e}")
    
    def get_user_insights(self, user_id: int) -> Dict:
        """Get personalized insights for user"""
        try:
            conn = self._get_connection()
            
            # Weak concepts
            weak_concepts_df = pd.read_sql('''
                SELECT concept, proficiency 
                FROM concept_mastery 
                WHERE user_id = ? AND proficiency < 70
                ORDER BY proficiency ASC
                LIMIT 5
            ''', conn, params=(user_id,))
            
            # Study patterns
            study_patterns_df = pd.read_sql('''
                SELECT strftime('%H', start_time) as hour, COUNT(*) as session_count
                FROM study_sessions 
                WHERE user_id = ?
                GROUP BY strftime('%H', start_time)
                ORDER BY session_count DESC
            ''', conn, params=(user_id,))
            
            # Progress trends
            progress_trends_df = pd.read_sql('''
                SELECT DATE(created_at) as date, 
                       AVG(CASE WHEN is_correct THEN 1 ELSE 0 END) as daily_accuracy
                FROM problem_history 
                WHERE user_id = ? AND created_at > date('now', '-30 days')
                GROUP BY DATE(created_at)
                ORDER BY date
            ''', conn, params=(user_id,))
            
            conn.close()
            
            return {
                'weak_concepts': weak_concepts_df.to_dict('records'),
                'study_patterns': study_patterns_df.to_dict('records'),
                'progress_trends': progress_trends_df.to_dict('records'),
                'recommendations': self._generate_recommendations(weak_concepts_df)
            }
            
        except Exception as e:
            logger.error(f"Error getting user insights: {e}")
            return {}
    
    def _generate_recommendations(self, weak_concepts_df) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        if not weak_concepts_df.empty:
            weak_concepts = [row['concept'] for row in weak_concepts_df.to_dict('records')]
            recommendations.append(f"Focus on practicing: {', '.join(weak_concepts[:3])}")
        
        # Add more recommendation logic based on various factors
        recommendations.extend([
            "Try solving problems with increasing difficulty",
            "Review previously solved problems to reinforce learning",
            "Set daily practice goals to maintain consistency"
        ])
        
        return recommendations
    
    # Admin and Reporting Methods
    def get_system_analytics(self) -> Dict:
        """Get system-wide analytics (for admin)"""
        try:
            conn = self._get_connection()
            
            # User statistics
            user_stats_df = pd.read_sql('''
                SELECT 
                    COUNT(*) as total_users,
                    COUNT(CASE WHEN last_login > datetime('now', '-7 days') THEN 1 END) as active_users_7d,
                    AVG(problems_solved) as avg_problems_solved,
                    AVG(total_study_time) as avg_study_time
                FROM user_progress
            ''', conn)
            
            # Popular concepts
            popular_concepts_df = pd.read_sql('''
                SELECT concept, COUNT(*) as practice_count
                FROM concept_mastery 
                GROUP BY concept 
                ORDER BY practice_count DESC 
                LIMIT 10
            ''', conn)
            
            # Daily activity
            daily_activity_df = pd.read_sql('''
                SELECT DATE(created_at) as date, COUNT(*) as problem_count
                FROM problem_history 
                WHERE created_at > datetime('now', '-30 days')
                GROUP BY DATE(created_at)
                ORDER BY date
            ''', conn)
            
            conn.close()
            
            return {
                'user_statistics': user_stats_df.to_dict('records')[0] if not user_stats_df.empty else {},
                'popular_concepts': popular_concepts_df.to_dict('records'),
                'daily_activity': daily_activity_df.to_dict('records')
            }
            
        except Exception as e:
            logger.error(f"Error getting system analytics: {e}")
            return {}
    
    # Backup and Maintenance
    def backup_database(self, backup_path: str) -> bool:
        """Create a backup of the database"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Database backed up to: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Error backing up database: {e}")
            return False
    
    def optimize_database(self):
        """Optimize database performance"""
        try:
            conn = self._get_connection()
            c = conn.cursor()
            
            # Vacuum to optimize storage
            c.execute('VACUUM')
            
            # Reindex for better performance
            c.execute('REINDEX')
            
            conn.commit()
            conn.close()
            
            logger.info("Database optimized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error optimizing database: {e}")
            return False

# Singleton instance
db_manager = DatabaseManager()

# Streamlit UI components for database management
def render_database_admin_panel():
    """Render admin panel for database management"""
    st.header("🔧 Database Administration")
    
    if not st.session_state.get('is_authenticated') or st.session_state.get('role') != 'admin':
        st.warning("Admin access required")
        return
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Analytics", "👥 User Management", "🗃️ Content", "🛠️ Maintenance"])
    
    with tab1:
        render_system_analytics()
    
    with tab2:
        render_user_management()
    
    with tab3:
        render_content_management()
    
    with tab4:
        render_maintenance_tools()

def render_system_analytics():
    """Render system analytics dashboard"""
    st.subheader("System Analytics")
    
    analytics = db_manager.get_system_analytics()
    
    if analytics:
        user_stats = analytics.get('user_statistics', {})
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Users", user_stats.get('total_users', 0))
        with col2:
            st.metric("Active Users (7d)", user_stats.get('active_users_7d', 0))
        with col3:
            st.metric("Avg Problems Solved", f"{user_stats.get('avg_problems_solved', 0):.1f}")
        with col4:
            st.metric("Avg Study Time (min)", f"{user_stats.get('avg_study_time', 0):.1f}")
        
        # Popular concepts
        st.subheader("Popular Concepts")
        popular_concepts = analytics.get('popular_concepts', [])
        if popular_concepts:
            for concept in popular_concepts[:5]:
                st.write(f"**{concept['concept']}**: {concept['practice_count']} practices")
        
        # Daily activity chart
        st.subheader("Daily Activity")
        daily_activity = analytics.get('daily_activity', [])
        if daily_activity:
            activity_df = pd.DataFrame(daily_activity)
            st.line_chart(activity_df.set_index('date')['problem_count'])

def render_user_management():
    """Render user management interface"""
    st.subheader("User Management")
    
    # This would typically include user search, edit, and management features
    st.info("User management features would be implemented here")

def render_content_management():
    """Render content management interface"""
    st.subheader("Content Management")
    
    # Formula management
    st.write("### Math Formulas")
    
    with st.form("add_formula"):
        st.write("Add New Formula")
        formula_name = st.text_input("Formula Name")
        formula_latex = st.text_input("LaTeX Expression")
        category = st.selectbox("Category", ["Algebra", "Geometry", "Calculus", "Statistics"])
        difficulty = st.selectbox("Difficulty", ["beginner", "intermediate", "advanced"])
        
        if st.form_submit_button("Add Formula"):
            if formula_name and formula_latex:
                success = db_manager.add_formula({
                    'formula_name': formula_name,
                    'formula_latex': formula_latex,
                    'category': category,
                    'difficulty': difficulty
                })
                if success:
                    st.success("Formula added successfully!")
                else:
                    st.error("Failed to add formula")

def render_maintenance_tools():
    """Render database maintenance tools"""
    st.subheader("Database Maintenance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Optimize Database", use_container_width=True):
            with st.spinner("Optimizing database..."):
                success = db_manager.optimize_database()
                if success:
                    st.success("Database optimized successfully!")
                else:
                    st.error("Failed to optimize database")
    
    with col2:
        if st.button("💾 Create Backup", use_container_width=True):
            backup_path = f"backup_{int(time.time())}.db"
            success = db_manager.backup_database(backup_path)
            if success:
                st.success(f"Backup created: {backup_path}")
            else:
                st.error("Failed to create backup")
    
    # Database info
    st.subheader("Database Information")
    try:
        conn = db_manager._get_connection()
        c = conn.cursor()
        
        # Get table sizes
        c.execute('''
            SELECT name FROM sqlite_master WHERE type='table'
        ''')
        tables = c.fetchall()
        
        for table in tables:
            table_name = table[0]
            c.execute(f'SELECT COUNT(*) FROM {table_name}')
            count = c.fetchone()[0]
            st.write(f"**{table_name}**: {count} records")
        
        conn.close()
    except Exception as e:
        st.error(f"Error getting database info: {e}")

# Example usage
if __name__ == "__main__":
    # Initialize and test the database
    db = DatabaseManager()
    
    # Test adding a user
    test_user = db.create_user(
        username="test_user",
        email="test@example.com", 
        password_hash="test_hash",
        salt="test_salt"
    )
    
    print(f"User created: {test_user}")
    
    # Test getting formulas
    formulas = db.get_formulas_by_category("Algebra")
    print(f"Found {len(formulas)} algebra formulas")