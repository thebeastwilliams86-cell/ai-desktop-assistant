"""
Web Integration Module
Provides enhanced web browsing, research, and content extraction capabilities
"""

import requests
import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import threading
import time
from urllib.parse import urljoin, urlparse
import hashlib

class WebResearchAssistant:
    """Enhanced web research and content extraction assistant"""
    
    def __init__(self, cache_dir='web_cache'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Configuration
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Research history and cache
        self.search_history = []
        self.content_cache = {}
        self.bookmarks = []
        
        # Load cached data
        self.load_cache()
        
        # Research templates
        self.research_templates = {
            'academic': {
                'sources': ['scholar.google.com', 'arxiv.org', 'researchgate.net'],
                'query_modifiers': ['pdf', 'research', 'study', 'paper']
            },
            'news': {
                'sources': ['news.google.com', 'bbc.com', 'cnn.com', 'reuters.com'],
                'query_modifiers': ['news', 'latest', 'breaking', 'update']
            },
            'technical': {
                'sources': ['stackoverflow.com', 'github.com', 'documentation', 'tutorial'],
                'query_modifiers': ['guide', 'how to', 'example', 'documentation']
            }
        }
    
    def load_cache(self):
        """Load cached web data"""
        try:
            cache_file = self.cache_dir / 'content_cache.json'
            if cache_file.exists():
                with open(cache_file, 'r') as f:
                    self.content_cache = json.load(f)
            
            bookmarks_file = self.cache_dir / 'bookmarks.json'
            if bookmarks_file.exists():
                with open(bookmarks_file, 'r') as f:
                    self.bookmarks = json.load(f)
        
        except Exception as e:
            print(f"Error loading web cache: {e}")
    
    def save_cache(self):
        """Save cached web data"""
        try:
            # Save content cache (limit size)
            cache_file = self.cache_dir / 'content_cache.json'
            if len(self.content_cache) > 1000:  # Limit cache size
                # Keep only most recent 1000 entries
                self.content_cache = dict(list(self.content_cache.items())[-1000:])
            
            with open(cache_file, 'w') as f:
                json.dump(self.content_cache, f, indent=2, default=str)
            
            # Save bookmarks
            bookmarks_file = self.cache_dir / 'bookmarks.json'
            with open(bookmarks_file, 'w') as f:
                json.dump(self.bookmarks, f, indent=2, default=str)
        
        except Exception as e:
            print(f"Error saving web cache: {e}")
    
    def intelligent_search(self, query: str, search_type: str = 'general', max_results: int = 10) -> Dict:
        """Perform intelligent web search with context awareness"""
        try:
            # Enhance query based on search type
            enhanced_query = self.enhance_query(query, search_type)
            
            # Generate cache key
            cache_key = hashlib.md5(f"{enhanced_query}_{search_type}_{max_results}".encode()).hexdigest()
            
            # Check cache first
            if cache_key in self.content_cache:
                cached_result = self.content_cache[cache_key]
                if self.is_cache_valid(cached_result.get('timestamp')):
                    cached_result['from_cache'] = True
                    self.search_history.append(cached_result)
                    return cached_result
            
            # Perform search (using DuckDuckGo for privacy)
            search_results = self.perform_duckduckgo_search(enhanced_query, max_results)
            
            # Process and enhance results
            processed_results = self.process_search_results(search_results, query, search_type)
            
            # Create result object
            result = {
                'query': query,
                'enhanced_query': enhanced_query,
                'search_type': search_type,
                'results': processed_results,
                'timestamp': datetime.now().isoformat(),
                'total_results': len(processed_results),
                'from_cache': False
            }
            
            # Cache result
            self.content_cache[cache_key] = result
            
            # Add to history
            self.search_history.append(result)
            
            # Save cache
            self.save_cache()
            
            return result
        
        except Exception as e:
            return {
                'error': str(e),
                'query': query,
                'search_type': search_type,
                'timestamp': datetime.now().isoformat()
            }
    
    def enhance_query(self, query: str, search_type: str) -> str:
        """Enhance search query based on type"""
        if search_type in self.research_templates:
            template = self.research_templates[search_type]
            
            # Add relevant modifiers based on query analysis
            query_lower = query.lower()
            
            # Check if query needs enhancement
            needs_modifier = True
            for modifier in template['query_modifiers']:
                if modifier in query_lower:
                    needs_modifier = False
                    break
            
            if needs_modifier and template['query_modifiers']:
                # Add the most relevant modifier
                modifier = template['query_modifiers'][0]
                query = f"{query} {modifier}"
            
            # Add site restrictions for academic/technical searches
            if search_type in ['academic', 'technical']:
                # Prioritize certain domains
                if search_type == 'academic':
                    query += f" site:{template['sources'][0]}"
                elif search_type == 'technical':
                    query += f" site:{template['sources'][0]}"
        
        return query
    
    def perform_duckduckgo_search(self, query: str, max_results: int) -> List[Dict]:
        """Perform search using DuckDuckGo"""
        try:
            # DuckDuckGo instant answers API
            url = "https://html.duckduckgo.com/html/"
            params = {
                'q': query,
                'kl': 'us-en'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            # Parse HTML results (simplified parsing)
            results = []
            html_content = response.text
            
            # Extract result blocks using regex
            result_pattern = r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>([^<]*)</a.*?<a[^>]*class="result__url"[^>]*>([^<]*)</a>'
            matches = re.findall(result_pattern, html_content, re.DOTALL)
            
            for match in matches[:max_results]:
                url, title, display_url = match
                
                # Clean up results
                title = re.sub(r'<[^>]*>', '', title).strip()
                display_url = re.sub(r'<[^>]*>', '', display_url).strip()
                
                # Try to get snippet
                snippet_pattern = f'<a[^>]*href="{url}"[^>]*>.*?</a>(.*?)<a[^>]*class="result__url"'
                snippet_match = re.search(snippet_pattern, html_content, re.DOTALL)
                snippet = ""
                if snippet_match:
                    snippet = re.sub(r'<[^>]*>', '', snippet_match.group(1)).strip()
                    snippet = snippet[:300] + "..." if len(snippet) > 300 else snippet
                
                results.append({
                    'title': title,
                    'url': url,
                    'display_url': display_url,
                    'snippet': snippet,
                    'source': 'DuckDuckGo'
                })
            
            return results
        
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def process_search_results(self, results: List[Dict], original_query: str, search_type: str) -> List[Dict]:
        """Process and enhance search results"""
        processed_results = []
        
        for result in results:
            try:
                # Calculate relevance score
                relevance_score = self.calculate_relevance(result, original_query, search_type)
                
                # Extract metadata
                domain = urlparse(result['url']).netloc
                
                enhanced_result = {
                    **result,
                    'domain': domain,
                    'relevance_score': relevance_score,
                    'content_type': self.detect_content_type(result),
                    'trust_score': self.calculate_trust_score(domain),
                    'extracted_date': self.extract_publish_date(result)
                }
                
                processed_results.append(enhanced_result)
            
            except Exception as e:
                print(f"Error processing result: {e}")
                continue
        
        # Sort by relevance score
        processed_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return processed_results
    
    def calculate_relevance(self, result: Dict, query: str, search_type: str) -> float:
        """Calculate relevance score for a search result"""
        score = 0.0
        query_words = query.lower().split()
        
        # Title relevance
        title_lower = result.get('title', '').lower()
        title_matches = sum(1 for word in query_words if word in title_lower)
        score += title_matches * 0.4
        
        # Snippet relevance
        snippet_lower = result.get('snippet', '').lower()
        snippet_matches = sum(1 for word in query_words if word in snippet_lower)
        score += snippet_matches * 0.3
        
        # URL relevance
        url_lower = result.get('url', '').lower()
        url_matches = sum(1 for word in query_words if word in url_lower)
        score += url_matches * 0.2
        
        # Domain authority (simplified)
        domain = urlparse(result.get('url', '')).netloc
        if any(trusted in domain for trusted in ['wikipedia', 'edu', 'gov', 'org']):
            score += 0.1
        
        return min(1.0, score)
    
    def detect_content_type(self, result: Dict) -> str:
        """Detect the type of content from search result"""
        url = result.get('url', '').lower()
        title = result.get('title', '').lower()
        snippet = result.get('snippet', '').lower()
        
        # Check for academic content
        if any(indicator in url or indicator in title for indicator in ['pdf', 'scholar', 'arxiv', 'research', 'paper']):
            return 'academic'
        
        # Check for news content
        if any(indicator in url for indicator in ['news', 'cnn', 'bbc', 'reuters']) or 'news' in title:
            return 'news'
        
        # Check for video content
        if any(indicator in url for indicator in ['youtube', 'vimeo', 'video']) or 'video' in title:
            return 'video'
        
        # Check for documentation
        if any(indicator in url or indicator in title for indicator in ['docs', 'documentation', 'tutorial', 'guide']):
            return 'documentation'
        
        # Check for forum/discussion
        if any(indicator in url for indicator in ['reddit', 'stackoverflow', 'forum']) or 'stack' in title:
            return 'discussion'
        
        return 'general'
    
    def calculate_trust_score(self, domain: str) -> float:
        """Calculate trust score for a domain"""
        # High trust domains
        high_trust = ['wikipedia.org', 'edu', 'gov', 'org', 'mit.edu', 'stanford.edu']
        
        # Medium trust domains
        medium_trust = ['reddit.com', 'stackoverflow.com', 'github.com']
        
        # Low trust indicators
        low_trust_indicators = ['blogspot', 'wordpress', 'tumblr']
        
        score = 0.5  # Base score
        
        if any(trusted in domain for trusted in high_trust):
            score = 0.9
        elif any(trusted in domain for trusted in medium_trust):
            score = 0.7
        elif any(indicator in domain for indicator in low_trust_indicators):
            score = 0.3
        
        return score
    
    def extract_publish_date(self, result: Dict) -> Optional[str]:
        """Extract publish date from search result"""
        # Look for date patterns in title and snippet
        date_patterns = [
            r'(\d{1,2}/\d{1,2}/\d{4})',
            r'(\d{4}-\d{2}-\d{2})',
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{1,2}, \d{4}'
        ]
        
        text = f"{result.get('title', '')} {result.get('snippet', '')}"
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return None
    
    def extract_content(self, url: str) -> Dict:
        """Extract and summarize content from a URL"""
        try:
            # Check cache first
            cache_key = hashlib.md5(url.encode()).hexdigest()
            if cache_key in self.content_cache:
                cached_content = self.content_cache[cache_key]
                if self.is_cache_valid(cached_content.get('timestamp')):
                    cached_content['from_cache'] = True
                    return cached_content
            
            # Fetch content
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            content = response.text
            
            # Extract main content (simplified extraction)
            extracted_content = self.extract_main_content(content)
            
            # Generate summary
            summary = self.generate_summary(extracted_content)
            
            # Extract key information
            key_info = self.extract_key_information(extracted_content)
            
            result = {
                'url': url,
                'title': self.extract_title(content),
                'content': extracted_content[:2000] + "..." if len(extracted_content) > 2000 else extracted_content,
                'summary': summary,
                'key_information': key_info,
                'word_count': len(extracted_content.split()),
                'timestamp': datetime.now().isoformat(),
                'from_cache': False
            }
            
            # Cache result
            self.content_cache[cache_key] = result
            
            return result
        
        except Exception as e:
            return {
                'error': str(e),
                'url': url,
                'timestamp': datetime.now().isoformat()
            }
    
    def extract_main_content(self, html_content: str) -> str:
        """Extract main content from HTML (simplified)"""
        # Remove script and style elements
        content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove HTML tags
        content = re.sub(r'<[^>]+>', ' ', content)
        
        # Clean up whitespace
        content = re.sub(r'\s+', ' ', content).strip()
        
        # Return first 2000 characters (in practice, you'd use more sophisticated extraction)
        return content[:2000]
    
    def extract_title(self, html_content: str) -> str:
        """Extract title from HTML"""
        title_match = re.search(r'<title[^>]*>([^<]*)</title>', html_content, re.IGNORECASE)
        if title_match:
            return title_match.group(1).strip()
        return "No title found"
    
    def generate_summary(self, content: str) -> str:
        """Generate a simple summary of content"""
        sentences = content.split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Simple extractive summarization - take first few sentences
        if len(sentences) > 0:
            summary_sentences = sentences[:3]
            return '. '.join(summary_sentences) + '.'
        
        return content[:200] + "..." if len(content) > 200 else content
    
    def extract_key_information(self, content: str) -> Dict:
        """Extract key information from content"""
        key_info = {
            'numbers': [],
            'dates': [],
            'names': [],  # Simplified - would use NLP in practice
            'keywords': []
        }
        
        # Extract numbers
        numbers = re.findall(r'\b\d+(?:,\d{3})*(?:\.\d+)?\b', content)
        key_info['numbers'] = numbers[:10]  # Limit to first 10
        
        # Extract dates
        dates = re.findall(r'\b\d{1,2}/\d{1,2}/\d{4}\b|\b\d{4}-\d{2}-\d{2}\b', content)
        key_info['dates'] = dates[:5]  # Limit to first 5
        
        # Extract keywords (simplified)
        words = content.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Ignore short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top 10 most frequent words
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        key_info['keywords'] = [word for word, freq in sorted_words[:10]]
        
        return key_info
    
    def is_cache_valid(self, timestamp: Optional[str], max_age_hours: int = 24) -> bool:
        """Check if cached data is still valid"""
        if not timestamp:
            return False
        
        try:
            cache_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            age = datetime.now() - cache_time
            return age.total_seconds() < max_age_hours * 3600
        except:
            return False
    
    def save_bookmark(self, url: str, title: str, tags: List[str] = None) -> Dict:
        """Save a bookmark"""
        bookmark = {
            'url': url,
            'title': title,
            'tags': tags or [],
            'timestamp': datetime.now().isoformat(),
            'id': hashlib.md5(url.encode()).hexdigest()
        }
        
        self.bookmarks.append(bookmark)
        self.save_cache()
        
        return bookmark
    
    def search_bookmarks(self, query: str) -> List[Dict]:
        """Search saved bookmarks"""
        query_lower = query.lower()
        results = []
        
        for bookmark in self.bookmarks:
            if (query_lower in bookmark['title'].lower() or 
                query_lower in bookmark['url'].lower() or
                any(query_lower in tag.lower() for tag in bookmark.get('tags', []))):
                results.append(bookmark)
        
        return results
    
    def get_research_summary(self, topic: str, max_sources: int = 5) -> Dict:
        """Generate comprehensive research summary for a topic"""
        try:
            # Perform broad search
            search_result = self.intelligent_search(topic, 'general', max_sources * 2)
            
            if 'error' in search_result:
                return search_result
            
            # Extract content from top results
            extracted_contents = []
            for result in search_result['results'][:max_sources]:
                content = self.extract_content(result['url'])
                if 'error' not in content:
                    extracted_contents.append(content)
            
            # Generate summary
            summary = self.generate_comprehensive_summary(extracted_contents, topic)
            
            return {
                'topic': topic,
                'sources_used': len(extracted_contents),
                'summary': summary,
                'source_urls': [content['url'] for content in extracted_contents],
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                'error': str(e),
                'topic': topic,
                'timestamp': datetime.now().isoformat()
            }
    
    def generate_comprehensive_summary(self, contents: List[Dict], topic: str) -> Dict:
        """Generate comprehensive summary from multiple sources"""
        if not contents:
            return {'summary': 'No content available for summarization.'}
        
        # Combine all summaries
        all_summaries = [content.get('summary', '') for content in contents]
        combined_text = ' '.join(all_summaries)
        
        # Extract key points from all sources
        all_key_info = []
        for content in contents:
            key_info = content.get('key_information', {})
            all_key_info.append(key_info)
        
        # Find common keywords
        all_keywords = []
        for key_info in all_key_info:
            all_keywords.extend(key_info.get('keywords', []))
        
        # Count keyword frequency
        keyword_freq = {}
        for keyword in all_keywords:
            keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1
        
        # Get most common keywords
        common_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'overview': combined_text[:500] + "..." if len(combined_text) > 500 else combined_text,
            'key_points': [kw[0] for kw in common_keywords[:5]],
            'common_keywords': [kw[0] for kw in common_keywords],
            'total_words': sum(content.get('word_count', 0) for content in contents),
            'source_count': len(contents)
        }