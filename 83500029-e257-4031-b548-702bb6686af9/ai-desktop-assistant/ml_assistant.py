"""
Machine Learning Assistant Module
Provides intelligent learning, prediction, and personalization capabilities
"""

import json
import pickle
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import threading
import time
from typing import Dict, List, Optional, Tuple
import hashlib

class LightweightMLAssistant:
    """Lightweight machine learning assistant for personalization and prediction"""
    
    def __init__(self, data_dir='ml_data'):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # User behavior tracking
        self.user_patterns = {
            'usage_times': {},
            'frequent_actions': {},
            'performance_preferences': {},
            'writing_style': {},
            'search_patterns': {}
        }
        
        # Learning data
        self.learning_data = {
            'system_usage': [],
            'user_actions': [],
            'preferences': {},
            'feedback_history': []
        }
        
        # Prediction models (simplified statistical models)
        self.prediction_models = {
            'usage_prediction': {},
            'performance_prediction': {},
            'recommendation_weights': {}
        }
        
        # Load existing data
        self.load_learning_data()
        
        # Start background learning thread
        self.learning_active = True
        self.learning_thread = threading.Thread(target=self.learning_loop, daemon=True)
        self.learning_thread.start()
    
    def load_learning_data(self):
        """Load existing learning data from files"""
        try:
            # Load user patterns
            patterns_file = self.data_dir / 'user_patterns.json'
            if patterns_file.exists():
                with open(patterns_file, 'r') as f:
                    self.user_patterns.update(json.load(f))
            
            # Load learning data
            learning_file = self.data_dir / 'learning_data.json'
            if learning_file.exists():
                with open(learning_file, 'r') as f:
                    data = json.load(f)
                    self.learning_data.update(data)
            
            # Load prediction models
            models_file = self.data_dir / 'prediction_models.pkl'
            if models_file.exists():
                with open(models_file, 'rb') as f:
                    self.prediction_models.update(pickle.load(f))
        
        except Exception as e:
            print(f"Error loading learning data: {e}")
    
    def save_learning_data(self):
        """Save learning data to files"""
        try:
            # Save user patterns
            patterns_file = self.data_dir / 'user_patterns.json'
            with open(patterns_file, 'w') as f:
                json.dump(self.user_patterns, f, indent=2, default=str)
            
            # Save learning data (keep last 1000 records to avoid bloat)
            learning_file = self.data_dir / 'learning_data.json'
            if len(self.learning_data.get('system_usage', [])) > 1000:
                self.learning_data['system_usage'] = self.learning_data['system_usage'][-1000:]
            if len(self.learning_data.get('user_actions', [])) > 1000:
                self.learning_data['user_actions'] = self.learning_data['user_actions'][-1000:]
            
            with open(learning_file, 'w') as f:
                json.dump(self.learning_data, f, indent=2, default=str)
            
            # Save prediction models
            models_file = self.data_dir / 'prediction_models.pkl'
            with open(models_file, 'wb') as f:
                pickle.dump(self.prediction_models, f)
        
        except Exception as e:
            print(f"Error saving learning data: {e}")
    
    def record_system_usage(self, cpu_usage: float, memory_usage: float, disk_usage: float):
        """Record system usage for pattern learning"""
        usage_data = {
            'timestamp': datetime.now().isoformat(),
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage,
            'disk_usage': disk_usage,
            'hour_of_day': datetime.now().hour,
            'day_of_week': datetime.now().weekday()
        }
        
        self.learning_data['system_usage'].append(usage_data)
        
        # Update usage patterns
        hour = datetime.now().hour
        if hour not in self.user_patterns['usage_times']:
            self.user_patterns['usage_times'][hour] = {
                'cpu_avg': 0,
                'memory_avg': 0,
                'count': 0
            }
        
        patterns = self.user_patterns['usage_times'][hour]
        patterns['count'] += 1
        patterns['cpu_avg'] = (patterns['cpu_avg'] * (patterns['count'] - 1) + cpu_usage) / patterns['count']
        patterns['memory_avg'] = (patterns['memory_avg'] * (patterns['count'] - 1) + memory_usage) / patterns['count']
    
    def record_user_action(self, action_type: str, action_data: Dict):
        """Record user action for learning"""
        action = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'action_data': action_data,
            'hour_of_day': datetime.now().hour,
            'day_of_week': datetime.now().weekday()
        }
        
        self.learning_data['user_actions'].append(action)
        
        # Update frequent actions
        if action_type not in self.user_patterns['frequent_actions']:
            self.user_patterns['frequent_actions'][action_type] = {}
        
        # Create a signature for the action
        action_signature = hashlib.md5(json.dumps(action_data, sort_keys=True).encode()).hexdigest()[:8]
        
        if action_signature not in self.user_patterns['frequent_actions'][action_type]:
            self.user_patterns['frequent_actions'][action_type][action_signature] = {
                'count': 0,
                'last_used': None,
                'data_sample': action_data
            }
        
        self.user_patterns['frequent_actions'][action_type][action_signature]['count'] += 1
        self.user_patterns['frequent_actions'][action_type][action_signature]['last_used'] = datetime.now().isoformat()
    
    def predict_optimal_cleanup_time(self) -> Dict:
        """Predict optimal time for system cleanup based on usage patterns"""
        try:
            if len(self.learning_data['system_usage']) < 24:  # Need at least 24 hours of data
                return {'recommendation': 'Need more usage data', 'confidence': 0}
            
            # Analyze usage by hour
            hourly_usage = {}
            for usage in self.learning_data['system_usage']:
                hour = usage['hour_of_day']
                if hour not in hourly_usage:
                    hourly_usage[hour] = []
                hourly_usage[hour].append(usage['cpu_usage'] + usage['memory_usage'])
            
            # Find hours with lowest usage
            avg_usage_by_hour = {}
            for hour, usages in hourly_usage.items():
                if len(usages) >= 3:  # Need at least 3 data points
                    avg_usage_by_hour[hour] = sum(usages) / len(usages)
            
            if not avg_usage_by_hour:
                return {'recommendation': 'Insufficient data for prediction', 'confidence': 0}
            
            # Find best time (lowest average usage)
            best_hour = min(avg_usage_by_hour.keys(), key=lambda x: avg_usage_by_hour[x])
            
            # Get confidence based on data variance
            usage_values = list(avg_usage_by_hour.values())
            if len(usage_values) > 1:
                variance = np.var(usage_values)
                max_usage = max(usage_values)
                min_usage = min(usage_values)
                confidence = min(0.9, (max_usage - min_usage) / max_usage)
            else:
                confidence = 0.5
            
            return {
                'recommended_hour': best_hour,
                'confidence': confidence,
                'reasoning': f'Hour {best_hour} typically has lowest system usage',
                'average_usage': avg_usage_by_hour.get(best_hour, 0)
            }
        
        except Exception as e:
            return {'error': str(e), 'confidence': 0}
    
    def get_personalized_recommendations(self, current_state: Dict) -> List[Dict]:
        """Get personalized recommendations based on learned patterns"""
        recommendations = []
        
        try:
            # Performance recommendations based on usage patterns
            if current_state.get('cpu_usage', 0) > 80:
                # Check if this is normal for this time
                current_hour = datetime.now().hour
                if current_hour in self.user_patterns['usage_times']:
                    normal_cpu = self.user_patterns['usage_times'][current_hour]['cpu_avg']
                    if current_state['cpu_usage'] > normal_cpu + 20:
                        recommendations.append({
                            'type': 'performance',
                            'priority': 'high',
                            'message': 'CPU usage is unusually high for this time',
                            'action': 'Consider closing unnecessary applications'
                        })
            
            # Usage pattern recommendations
            frequent_actions = self.user_patterns.get('frequent_actions', {})
            for action_type, actions in frequent_actions.items():
                if action_type == 'cleanup':
                    most_common = max(actions.items(), key=lambda x: x[1]['count'])
                    if most_common[1]['count'] > 5:  # If performed more than 5 times
                        recommendations.append({
                            'type': 'automation',
                            'priority': 'medium',
                            'message': f'You frequently perform {action_type} operations',
                            'action': 'Consider setting up automatic scheduling'
                        })
            
            # Writing assistance recommendations
            if 'writing' in frequent_actions:
                writing_actions = frequent_actions['writing']
                if len(writing_actions) > 0:
                    most_common_style = max(writing_actions.items(), key=lambda x: x[1]['count'])
                    recommendations.append({
                        'type': 'writing',
                        'priority': 'low',
                        'message': 'Writing pattern detected',
                        'action': 'I can help optimize your writing environment based on your preferences'
                    })
            
            # Time-based recommendations
            current_hour = datetime.now().hour
            if 22 <= current_hour <= 6:  # Late night/early morning
                recommendations.append({
                    'type': 'maintenance',
                    'priority': 'low',
                    'message': 'It\'s late - consider running maintenance tasks',
                    'action': 'This might be a good time for system cleanup or updates'
                })
        
        except Exception as e:
            recommendations.append({
                'type': 'error',
                'priority': 'low',
                'message': f'Error generating recommendations: {e}',
                'action': 'Continue monitoring'
            })
        
        return recommendations
    
    def learn_writing_style(self, text: str, document_type: str = 'general'):
        """Learn from user's writing style"""
        try:
            # Analyze text characteristics
            words = text.split()
            sentences = text.split('.')
            
            style_features = {
                'avg_sentence_length': len(words) / max(1, len(sentences)),
                'avg_word_length': sum(len(word) for word in words) / max(1, len(words)),
                'paragraph_count': len(text.split('\n\n')),
                'formality_score': self._calculate_formality(text),
                'complexity_score': self._calculate_complexity(text),
                'document_type': document_type,
                'timestamp': datetime.now().isoformat()
            }
            
            # Update writing style patterns
            if document_type not in self.user_patterns['writing_style']:
                self.user_patterns['writing_style'][document_type] = []
            
            self.user_patterns['writing_style'][document_type].append(style_features)
            
            # Keep only last 50 samples per document type
            if len(self.user_patterns['writing_style'][document_type]) > 50:
                self.user_patterns['writing_style'][document_type] = self.user_patterns['writing_style'][document_type][-50:]
            
            return style_features
        
        except Exception as e:
            return {'error': str(e)}
    
    def _calculate_formality(self, text: str) -> float:
        """Calculate formality score of text (0-1, higher = more formal)"""
        informal_words = ['yeah', 'okay', 'cool', 'awesome', 'great', 'bad', 'good', 'nice', 'really', 'very']
        formal_words = ['furthermore', 'however', 'therefore', 'consequently', 'additionally', 'nevertheless']
        
        words = text.lower().split()
        informal_count = sum(1 for word in words if word in informal_words)
        formal_count = sum(1 for word in words if word in formal_words)
        
        total_words = len(words)
        if total_words == 0:
            return 0.5
        
        # Simple formality calculation
        formality = 0.5 + (formal_count - informal_count) / total_words
        return max(0, min(1, formality))
    
    def _calculate_complexity(self, text: str) -> float:
        """Calculate text complexity score (0-1, higher = more complex)"""
        words = text.split()
        sentences = text.split('.')
        
        if len(sentences) == 0:
            return 0.5
        
        # Average sentence length
        avg_sentence_length = len(words) / len(sentences)
        
        # Word length complexity
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        # Normalize and combine
        length_score = min(1, avg_sentence_length / 25)  # Normalize by 25 words per sentence
        word_score = min(1, avg_word_length / 8)  # Normalize by 8 characters per word
        
        return (length_score + word_score) / 2
    
    def get_writing_suggestions(self, text: str, document_type: str = 'general') -> List[str]:
        """Get writing suggestions based on learned style"""
        suggestions = []
        
        try:
            # Analyze current text
            current_style = self.learn_writing_style(text, document_type)
            
            # Get historical patterns
            if document_type in self.user_patterns['writing_style'] and len(self.user_patterns['writing_style'][document_type]) > 5:
                historical_styles = self.user_patterns['writing_style'][document_type][-5:]  # Last 5 samples
                
                # Calculate averages
                avg_sentence_length = sum(s['avg_sentence_length'] for s in historical_styles) / len(historical_styles)
                avg_formality = sum(s['formality_score'] for s in historical_styles) / len(historical_styles)
                avg_complexity = sum(s['complexity_score'] for s in historical_styles) / len(historical_styles)
                
                # Compare with current
                if abs(current_style['avg_sentence_length'] - avg_sentence_length) > 5:
                    if current_style['avg_sentence_length'] > avg_sentence_length:
                        suggestions.append("Consider using shorter sentences for better readability")
                    else:
                        suggestions.append("Your sentences are shorter than usual - consider more detailed descriptions")
                
                if abs(current_style['formality_score'] - avg_formality) > 0.3:
                    if current_style['formality_score'] < avg_formality:
                        suggestions.append("Consider using more formal language for this type of document")
                    else:
                        suggestions.append("Your writing is quite formal - consider adding more conversational elements")
                
                if abs(current_style['complexity_score'] - avg_complexity) > 0.3:
                    if current_style['complexity_score'] > avg_complexity:
                        suggestions.append("Consider simplifying complex sentences for clarity")
                    else:
                        suggestions.append("You could add more sophisticated vocabulary and sentence structures")
            
            # General writing suggestions
            words = text.split()
            if len(words) < 50:
                suggestions.append("Consider expanding your content with more details")
            
            sentences = text.split('.')
            avg_words_per_sentence = len(words) / max(1, len(sentences))
            if avg_words_per_sentence > 25:
                suggestions.append("Some sentences are quite long - consider breaking them up for readability")
            elif avg_words_per_sentence < 10:
                suggestions.append("Consider combining some short sentences for better flow")
        
        except Exception as e:
            suggestions.append(f"Error generating suggestions: {e}")
        
        return suggestions
    
    def predict_performance_issues(self) -> List[Dict]:
        """Predict potential performance issues based on patterns"""
        predictions = []
        
        try:
            if len(self.learning_data['system_usage']) < 48:  # Need at least 2 days of data
                return predictions
            
            # Analyze recent trends
            recent_usage = self.learning_data['system_usage'][-24:]  # Last 24 hours
            older_usage = self.learning_data['system_usage'][-48:-24]  # Previous 24 hours
            
            # Calculate averages
            recent_cpu_avg = sum(u['cpu_usage'] for u in recent_usage) / len(recent_usage)
            older_cpu_avg = sum(u['cpu_usage'] for u in older_usage) / len(older_usage)
            
            recent_memory_avg = sum(u['memory_usage'] for u in recent_usage) / len(recent_usage)
            older_memory_avg = sum(u['memory_usage'] for u in older_usage) / len(older_usage)
            
            # Predict issues based on trends
            if recent_cpu_avg > older_cpu_avg + 10:
                predictions.append({
                    'type': 'cpu_trend',
                    'severity': 'medium',
                    'message': 'CPU usage has been increasing recently',
                    'prediction': 'May reach critical levels in next 24 hours',
                    'suggestion': 'Consider identifying and managing high CPU processes'
                })
            
            if recent_memory_avg > older_memory_avg + 10:
                predictions.append({
                    'type': 'memory_trend',
                    'severity': 'medium',
                    'message': 'Memory usage has been increasing recently',
                    'prediction': 'May need memory cleanup soon',
                    'suggestion': 'Check for memory leaks or restart applications'
                })
            
            # Check for time-based patterns
            current_hour = datetime.now().hour
            if current_hour in self.user_patterns['usage_times']:
                expected_cpu = self.user_patterns['usage_times'][current_hour]['cpu_avg']
                expected_memory = self.user_patterns['usage_times'][current_hour]['memory_avg']
                
                if expected_cpu > 80:
                    predictions.append({
                        'type': 'time_based_cpu',
                        'severity': 'low',
                        'message': f'High CPU usage typically expected at this time (hour {current_hour})',
                        'prediction': 'System may run slowly',
                        'suggestion': 'Schedule intensive tasks for different times if possible'
                    })
        
        except Exception as e:
            predictions.append({
                'type': 'error',
                'severity': 'low',
                'message': f'Error in performance prediction: {e}',
                'suggestion': 'Continue monitoring system normally'
            })
        
        return predictions
    
    def learning_loop(self):
        """Background learning loop"""
        while self.learning_active:
            try:
                # Save learning data periodically
                self.save_learning_data()
                
                # Clean old data
                if len(self.learning_data['system_usage']) > 2000:
                    self.learning_data['system_usage'] = self.learning_data['system_usage'][-1000:]
                if len(self.learning_data['user_actions']) > 2000:
                    self.learning_data['user_actions'] = self.learning_data['user_actions'][-1000:]
                
                # Sleep for 5 minutes
                time.sleep(300)
            
            except Exception as e:
                print(f"Error in learning loop: {e}")
                time.sleep(60)
    
    def shutdown(self):
        """Shutdown the ML assistant"""
        self.learning_active = False
        self.save_learning_data()
        if self.learning_thread.is_alive():
            self.learning_thread.join(timeout=5)
    
    def get_learning_summary(self) -> Dict:
        """Get summary of learned patterns"""
        try:
            summary = {
                'data_points_collected': {
                    'system_usage': len(self.learning_data['system_usage']),
                    'user_actions': len(self.learning_data['user_actions']),
                    'feedback_history': len(self.learning_data['feedback_history'])
                },
                'learned_patterns': {
                    'usage_patterns_hours': len(self.user_patterns['usage_times']),
                    'frequent_actions_types': len(self.user_patterns['frequent_actions']),
                    'writing_styles_document_types': len(self.user_patterns['writing_style'])
                },
                'prediction_accuracy': {
                    'cleanup_time_prediction': 'Collecting data...',
                    'performance_prediction': 'Collecting data...'
                },
                'recommendations_generated': 0,  # Would track this in practice
                'learning_start_date': min([item['timestamp'] for item in self.learning_data['system_usage']], default='No data'),
                'last_updated': datetime.now().isoformat()
            }
            
            return summary
        
        except Exception as e:
            return {'error': str(e)}