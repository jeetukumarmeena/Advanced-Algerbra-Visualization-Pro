import sqlite3
import time
import json
from datetime import datetime, timedelta

class GamificationEngine:
    def __init__(self, db_path="data/user_progress.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # User progress table
        c.execute('''CREATE TABLE IF NOT EXISTS user_progress
                    (user_id TEXT PRIMARY KEY,
                     total_points INTEGER DEFAULT 0,
                     current_level INTEGER DEFAULT 1,
                     problems_attempted INTEGER DEFAULT 0,
                     problems_solved INTEGER DEFAULT 0,
                     streak_days INTEGER DEFAULT 0,
                     last_active DATE,
                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        # Concept mastery table
        c.execute('''CREATE TABLE IF NOT EXISTS concept_mastery
                    (user_id TEXT,
                     concept TEXT,
                     proficiency REAL DEFAULT 0,
                     problems_attempted INTEGER DEFAULT 0,
                     problems_solved INTEGER DEFAULT 0,
                     last_practiced DATE,
                     PRIMARY KEY (user_id, concept))''')
        
        # Achievements table
        c.execute('''CREATE TABLE IF NOT EXISTS achievements
                    (user_id TEXT,
                     achievement_id TEXT,
                     achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                     PRIMARY KEY (user_id, achievement_id))''')
        
        conn.commit()
        conn.close()
    
    def _init_user_progress(self, user_id):
        """Initialize user progress for new user"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        try:
            # Ensure user_id is string
            user_id_str = str(user_id)
            c.execute('''INSERT OR IGNORE INTO user_progress 
                        (user_id, total_points, current_level, problems_attempted, problems_solved, streak_days, last_active)
                        VALUES (?, 0, 1, 0, 0, 0, DATE('now'))''', (user_id_str,))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error initializing user progress: {e}")
            return False
        finally:
            conn.close()
    
    def get_levels(self):
        """Define level progression"""
        return {
            1: {"name": "Algebra Novice", "points_required": 0, "color": "#6B7280"},
            2: {"name": "Equation Explorer", "points_required": 100, "color": "#10B981"},
            3: {"name": "Polynomial Pro", "points_required": 300, "color": "#3B82F6"},
            4: {"name": "Algebra Master", "points_required": 600, "color": "#8B5CF6"},
            5: {"name": "Math Genius", "points_required": 1000, "color": "#F59E0B"}
        }
    
    def get_achievements(self):
        """Define available achievements"""
        return {
            "first_problem": {"name": "First Steps", "description": "Solve your first problem", "points": 10},
            "quick_learner": {"name": "Quick Learner", "description": "Solve 10 problems in one day", "points": 25},
            "algebra_expert": {"name": "Algebra Expert", "description": "Master all basic algebra concepts", "points": 50},
            "streak_master": {"name": "Consistent Learner", "description": "Maintain a 7-day streak", "points": 30},
            "speed_demon": {"name": "Speed Demon", "description": "Solve 5 problems in under 5 minutes", "points": 40}
        }
    
    def update_user_progress(self, user_id, concept, difficulty, solved_correctly, time_taken=None):
        """Update user progress after problem attempt"""
        # Ensure user_id is string
        user_id_str = str(user_id)
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Ensure user progress exists
        self._init_user_progress(user_id_str)
        
        # Calculate points
        base_points = difficulty * 10
        if solved_correctly:
            points_earned = base_points
            if time_taken and time_taken < 60:  # Bonus for speed
                points_earned += 5
        else:
            points_earned = base_points * 0.1  # Partial points for attempts
        
        # Update user progress
        c.execute('''UPDATE user_progress 
                    SET total_points = total_points + ?,
                        problems_attempted = problems_attempted + 1,
                        problems_solved = problems_solved + ?,
                        last_active = DATE('now')
                    WHERE user_id = ?''',
                 (points_earned, 1 if solved_correctly else 0, user_id_str))
        
        # Update concept mastery
        c.execute('''INSERT OR REPLACE INTO concept_mastery 
                    (user_id, concept, proficiency, problems_attempted, problems_solved, last_practiced)
                    VALUES (?, ?, 
                            COALESCE((SELECT proficiency FROM concept_mastery WHERE user_id = ? AND concept = ?), 0) + ?,
                            COALESCE((SELECT problems_attempted FROM concept_mastery WHERE user_id = ? AND concept = ?), 0) + 1,
                            COALESCE((SELECT problems_solved FROM concept_mastery WHERE user_id = ? AND concept = ?), 0) + ?,
                            DATE('now'))''',
                 (user_id_str, concept, user_id_str, concept, points_earned/10, 
                  user_id_str, concept, user_id_str, concept, 1 if solved_correctly else 0))
        
        # Check for achievements
        self._check_achievements(user_id_str, c)
        
        conn.commit()
        
        # Get updated user data
        user_data = self.get_user_data(user_id_str)
        conn.close()
        
        return user_data, points_earned
    
    def _check_achievements(self, user_id, cursor):
        """Check and award new achievements"""
        achievements = self.get_achievements()
        
        # Check first problem achievement
        cursor.execute('SELECT problems_solved FROM user_progress WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        if result and result[0] == 1:
            self._award_achievement(user_id, "first_problem", cursor)
        
        # Check streak achievement
        cursor.execute('SELECT streak_days FROM user_progress WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        if result and result[0] >= 7:
            self._award_achievement(user_id, "streak_master", cursor)
    
    def _award_achievement(self, user_id, achievement_id, cursor):
        """Award an achievement to user"""
        try:
            cursor.execute('INSERT INTO achievements (user_id, achievement_id) VALUES (?, ?)',
                         (user_id, achievement_id))
            
            # Add achievement points to total
            achievement = self.get_achievements()[achievement_id]
            cursor.execute('UPDATE user_progress SET total_points = total_points + ? WHERE user_id = ?',
                         (achievement["points"], user_id))
        except sqlite3.IntegrityError:
            pass  # Achievement already awarded
    
    def get_user_data(self, user_id):
        """Get comprehensive user data"""
        # Ensure user_id is string
        user_id_str = str(user_id)
        
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Ensure user progress exists
        self._init_user_progress(user_id_str)
        
        # Basic user progress
        c.execute('SELECT * FROM user_progress WHERE user_id = ?', (user_id_str,))
        user_progress = c.fetchone()
        
        if not user_progress:
            conn.close()
            return None
        
        # Concept mastery
        c.execute('SELECT concept, proficiency FROM concept_mastery WHERE user_id = ? ORDER BY proficiency DESC', (user_id_str,))
        concept_mastery = c.fetchall()
        
        # Achievements
        c.execute('''SELECT a.achievement_id, a.achieved_at 
                    FROM achievements a 
                    WHERE a.user_id = ?''', (user_id_str,))
        user_achievements = c.fetchall()
        
        conn.close()
        
        # Calculate current level
        levels = self.get_levels()
        total_points = user_progress[1]
        current_level = 1
        for level, data in levels.items():
            if total_points >= data["points_required"]:
                current_level = level
        
        return {
            "user_id": user_progress[0],
            "total_points": total_points,
            "current_level": current_level,
            "level_data": levels[current_level],
            "problems_attempted": user_progress[3],
            "problems_solved": user_progress[4],
            "streak_days": user_progress[5],
            "concept_mastery": dict(concept_mastery),
            "achievements": [ach[0] for ach in user_achievements]
        }

# Global instance
game_engine = GamificationEngine()