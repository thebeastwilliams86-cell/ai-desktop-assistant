#!/usr/bin/env python3
"""
AI Desktop Assistant - Lightweight System Monitor and Optimization Tool
Features: System monitoring, performance optimization, web integration, and writing assistance
"""

import os
import sys
import json
import time
import psutil
import platform
import subprocess
import threading
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import webbrowser
import requests
from typing import Dict, List, Tuple, Optional

class SystemMonitor:
    """Core system monitoring functionality"""
    
    def __init__(self):
        self.monitoring = False
        self.metrics_history = []
        self.alerts = []
        
    def get_cpu_info(self) -> Dict:
        """Get CPU information and usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_freq = psutil.cpu_freq()
            cpu_temp = self._get_cpu_temperature()
            cpu_count = psutil.cpu_count()
            
            return {
                'usage_percent': cpu_percent,
                'frequency_mhz': cpu_freq.current if cpu_freq else 0,
                'temperature_celsius': cpu_temp,
                'core_count': cpu_count,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _get_cpu_temperature(self) -> Optional[float]:
        """Get CPU temperature (platform-specific)"""
        try:
            if platform.system() == "Windows":
                # Windows temperature monitoring would require additional libraries
                return None
            elif platform.system() == "Linux":
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        if any(keyword in name.lower() for keyword in ['cpu', 'core', 'tctl', 'temp']):
                            return entries[0].current
                return None
            elif platform.system() == "Darwin":  # macOS
                result = subprocess.run(['sudo', 'powermetrics', '--samplers', 'cpu_power', '-i', '1', '-n', '1'], 
                                      capture_output=True, text=True)
                # Parse temperature from powermetrics output
                return None  # Would need additional parsing
        except:
            return None
    
    def get_memory_info(self) -> Dict:
        """Get RAM usage information"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                'total_gb': round(memory.total / (1024**3), 2),
                'available_gb': round(memory.available / (1024**3), 2),
                'used_gb': round(memory.used / (1024**3), 2),
                'usage_percent': memory.percent,
                'swap_total_gb': round(swap.total / (1024**3), 2),
                'swap_used_gb': round(swap.used / (1024**3), 2),
                'swap_percent': swap.percent,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_disk_info(self) -> List[Dict]:
        """Get disk usage information for all drives"""
        try:
            disks = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_info = {
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total_gb': round(usage.total / (1024**3), 2),
                        'used_gb': round(usage.used / (1024**3), 2),
                        'free_gb': round(usage.free / (1024**3), 2),
                        'usage_percent': round((usage.used / usage.total) * 100, 2),
                        'timestamp': datetime.now().isoformat()
                    }
                    disks.append(disk_info)
                except PermissionError:
                    continue
            return disks
        except Exception as e:
            return [{'error': str(e)}]
    
    def get_network_info(self) -> Dict:
        """Get network information"""
        try:
            net_io = psutil.net_io_counters()
            net_connections = len(psutil.net_connections())
            
            return {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'active_connections': net_connections,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_running_processes(self) -> List[Dict]:
        """Get information about running processes"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
            return processes[:20]  # Return top 20 processes
        except Exception as e:
            return [{'error': str(e)}]

class SystemOptimizer:
    """System optimization and maintenance tools"""
    
    def __init__(self):
        self.optimization_history = []
    
    def check_software_updates(self) -> Dict:
        """Check for available software updates"""
        try:
            platform_system = platform.system()
            update_info = {'platform': platform_system, 'updates_available': []}
            
            if platform_system == "Windows":
                # Check for Windows updates
                result = subprocess.run(['powershell', '-Command', 
                    'Get-WUList -MicrosoftUpdate | Select-Object Title'], 
                    capture_output=True, text=True)
                if result.returncode == 0:
                    update_info['updates_available'] = result.stdout.strip().split('\n')
            
            elif platform_system == "Linux":
                # Check for package updates (apt-based systems)
                result = subprocess.run(['apt', 'list', '--upgradable'], 
                    capture_output=True, text=True)
                if result.returncode == 0:
                    updates = [line.split('/')[0] for line in result.stdout.strip().split('\n') if line]
                    update_info['updates_available'] = updates
            
            elif platform_system == "Darwin":
                # Check for macOS updates
                result = subprocess.run(['softwareupdate', '-l'], 
                    capture_output=True, text=True)
                update_info['updates_available'] = result.stdout.strip()
            
            update_info['timestamp'] = datetime.now().isoformat()
            return update_info
            
        except Exception as e:
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def cleanup_browser_cache(self) -> Dict:
        """Clean browser cache files"""
        try:
            cleaned_files = 0
            space_freed = 0
            
            platform_system = platform.system()
            user_home = Path.home()
            
            # Chrome cache cleanup
            chrome_paths = [
                user_home / "AppData/Local/Google/Chrome/User Data/Default/Cache",
                user_home / ".cache/google-chrome/Default/Cache",
                user_home / "Library/Caches/Google/Chrome/Default/Cache"
            ]
            
            for cache_path in chrome_paths:
                if cache_path.exists():
                    try:
                        for file in cache_path.rglob('*'):
                            if file.is_file():
                                file_size = file.stat().st_size
                                file.unlink()
                                cleaned_files += 1
                                space_freed += file_size
                    except PermissionError:
                        continue
            
            return {
                'files_cleaned': cleaned_files,
                'space_freed_mb': round(space_freed / (1024**2), 2),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def analyze_startup_programs(self) -> List[Dict]:
        """Analyze startup programs"""
        try:
            startup_programs = []
            platform_system = platform.system()
            
            if platform_system == "Windows":
                # Windows startup programs
                import winreg
                startup_keys = [
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
                    r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"
                ]
                
                for key_path in startup_keys:
                    try:
                        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                            i = 0
                            while True:
                                name, value, _ = winreg.EnumValue(key, i)
                                startup_programs.append({
                                    'name': name,
                                    'command': value,
                                    'source': 'Registry',
                                    'user_specific': True
                                })
                                i += 1
                    except WindowsError:
                        break
            
            elif platform_system == "Linux":
                # Linux systemd services
                result = subprocess.run(['systemctl', 'list-unit-files', '--state=enabled', '--type=service'], 
                    capture_output=True, text=True)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'service' in line and 'enabled' in line:
                            service_name = line.split('.')[0].strip()
                            startup_programs.append({
                                'name': service_name,
                                'command': f'systemctl start {service_name}',
                                'source': 'systemd',
                                'user_specific': False
                            })
            
            return startup_programs
            
        except Exception as e:
            return [{'error': str(e)}]

class WebAssistant:
    """Web browsing and research assistant"""
    
    def __init__(self):
        self.search_history = []
        self.session_data = {}
    
    def web_search(self, query: str, num_results: int = 5) -> Dict:
        """Perform web search (simplified version)"""
        try:
            # Using a simple approach - in real implementation, you'd use a proper search API
            search_url = f"https://duckduckgo.com/html/?q={query}"
            
            # For demonstration, we'll return a structured response
            # In practice, you'd parse actual search results
            
            result = {
                'query': query,
                'results': [
                    {
                        'title': f'Search result for: {query}',
                        'url': 'https://example.com',
                        'snippet': f'Information about {query}',
                        'relevance_score': 0.9
                    }
                ],
                'timestamp': datetime.now().isoformat()
            }
            
            self.search_history.append(result)
            return result
            
        except Exception as e:
            return {'error': str(e), 'query': query}

class WritingAssistant:
    """Writing and content creation assistant"""
    
    def __init__(self):
        self.documents = []
        self.templates = {}
        self.learning_data = {}
    
    def create_document(self, title: str, content_type: str = "general") -> Dict:
        """Create a new document"""
        try:
            doc_id = len(self.documents) + 1
            document = {
                'id': doc_id,
                'title': title,
                'content_type': content_type,
                'content': '',
                'created_at': datetime.now().isoformat(),
                'last_modified': datetime.now().isoformat(),
                'word_count': 0,
                'character_count': 0
            }
            
            self.documents.append(document)
            return document
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_content(self, text: str) -> Dict:
        """Analyze text content"""
        try:
            words = text.split()
            sentences = text.split('.')
            paragraphs = text.split('\n\n')
            
            analysis = {
                'word_count': len(words),
                'sentence_count': len([s for s in sentences if s.strip()]),
                'paragraph_count': len([p for p in paragraphs if p.strip()]),
                'character_count': len(text),
                'character_count_no_spaces': len(text.replace(' ', '')),
                'avg_words_per_sentence': round(len(words) / len([s for s in sentences if s.strip()]), 2) if sentences else 0,
                'reading_time_minutes': round(len(words) / 200, 1),  # Average reading speed
                'sentiment': 'neutral'  # Simplified - would use NLP library in practice
            }
            
            return analysis
            
        except Exception as e:
            return {'error': str(e)}

class AIDesktopAssistant:
    """Main AI Desktop Assistant application"""
    
    def __init__(self):
        self.system_monitor = SystemMonitor()
        self.system_optimizer = SystemOptimizer()
        self.web_assistant = WebAssistant()
        self.writing_assistant = WritingAssistant()
        
        self.root = tk.Tk()
        self.setup_ui()
        
        # Start monitoring thread
        self.monitoring_thread = None
        self.start_monitoring()
    
    def setup_ui(self):
        """Setup the main user interface"""
        self.root.title("AI Desktop Assistant")
        self.root.geometry("1200x800")
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # System Monitor Tab
        self.monitor_frame = ttk.Frame(notebook)
        notebook.add(self.monitor_frame, text="System Monitor")
        self.setup_monitor_tab()
        
        # Optimization Tab
        self.optimize_frame = ttk.Frame(notebook)
        notebook.add(self.optimize_frame, text="Optimization")
        self.setup_optimization_tab()
        
        # Web Assistant Tab
        self.web_frame = ttk.Frame(notebook)
        notebook.add(self.web_frame, text="Web Assistant")
        self.setup_web_tab()
        
        # Writing Assistant Tab
        self.writing_frame = ttk.Frame(notebook)
        notebook.add(self.writing_frame, text="Writing Assistant")
        self.setup_writing_tab()
    
    def setup_monitor_tab(self):
        """Setup system monitoring tab"""
        # Create frame for metrics
        metrics_frame = ttk.LabelFrame(self.monitor_frame, text="System Metrics", padding=10)
        metrics_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # CPU Info
        cpu_frame = ttk.Frame(metrics_frame)
        cpu_frame.pack(fill='x', pady=5)
        ttk.Label(cpu_frame, text="CPU Usage:", font=('Arial', 10, 'bold')).pack(side='left')
        self.cpu_label = ttk.Label(cpu_frame, text="0%")
        self.cpu_label.pack(side='left', padx=10)
        
        # Memory Info
        memory_frame = ttk.Frame(metrics_frame)
        memory_frame.pack(fill='x', pady=5)
        ttk.Label(memory_frame, text="RAM Usage:", font=('Arial', 10, 'bold')).pack(side='left')
        self.memory_label = ttk.Label(memory_frame, text="0%")
        self.memory_label.pack(side='left', padx=10)
        
        # Disk Info
        disk_frame = ttk.Frame(metrics_frame)
        disk_frame.pack(fill='x', pady=5)
        ttk.Label(disk_frame, text="Disk Usage:", font=('Arial', 10, 'bold')).pack(side='left')
        self.disk_label = ttk.Label(disk_label, text="0%")
        self.disk_label.pack(side='left', padx=10)
        
        # Process List
        process_frame = ttk.LabelFrame(metrics_frame, text="Top Processes", padding=5)
        process_frame.pack(fill='both', expand=True, pady=10)
        
        # Create treeview for processes
        columns = ('Name', 'CPU %', 'Memory %', 'Status')
        self.process_tree = ttk.Treeview(process_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.process_tree.heading(col, text=col)
            self.process_tree.column(col, width=150)
        
        self.process_tree.pack(fill='both', expand=True)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(process_frame, orient='vertical', command=self.process_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.process_tree.configure(yscrollcommand=scrollbar.set)
    
    def setup_optimization_tab(self):
        """Setup system optimization tab"""
        # Create buttons for optimization tasks
        button_frame = ttk.Frame(self.optimize_frame)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(button_frame, text="Check Updates", command=self.check_updates).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Clean Browser Cache", command=self.clean_cache).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Analyze Startup", command=self.analyze_startup).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Disk Cleanup", command=self.disk_cleanup).pack(side='left', padx=5)
        
        # Results area
        results_frame = ttk.LabelFrame(self.optimize_frame, text="Optimization Results", padding=10)
        results_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.optimize_text = scrolledtext.ScrolledText(results_frame, height=20, width=80)
        self.optimize_text.pack(fill='both', expand=True)
    
    def setup_web_tab(self):
        """Setup web assistant tab"""
        # Search input
        search_frame = ttk.Frame(self.web_frame)
        search_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(search_frame, text="Search:").pack(side='left')
        self.search_entry = ttk.Entry(search_frame, width=50)
        self.search_entry.pack(side='left', padx=5)
        ttk.Button(search_frame, text="Search", command=self.perform_search).pack(side='left')
        
        # Results area
        web_results_frame = ttk.LabelFrame(self.web_frame, text="Search Results", padding=10)
        web_results_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.web_text = scrolledtext.ScrolledText(web_results_frame, height=20, width=80)
        self.web_text.pack(fill='both', expand=True)
    
    def setup_writing_tab(self):
        """Setup writing assistant tab"""
        # Document creation
        doc_frame = ttk.Frame(self.writing_frame)
        doc_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(doc_frame, text="Document Title:").pack(side='left')
        self.doc_title_entry = ttk.Entry(doc_frame, width=30)
        self.doc_title_entry.pack(side='left', padx=5)
        
        ttk.Label(doc_frame, text="Type:").pack(side='left', padx=(10, 0))
        self.doc_type_combo = ttk.Combobox(doc_frame, values=['general', 'book', 'article', 'notes'], width=15)
        self.doc_type_combo.set('general')
        self.doc_type_combo.pack(side='left', padx=5)
        
        ttk.Button(doc_frame, text="Create Document", command=self.create_document).pack(side='left', padx=5)
        
        # Writing area
        writing_frame = ttk.LabelFrame(self.writing_frame, text="Writing Area", padding=10)
        writing_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.writing_text = scrolledtext.ScrolledText(writing_frame, height=15, width=80)
        self.writing_text.pack(fill='both', expand=True)
        
        # Analysis button
        ttk.Button(writing_frame, text="Analyze Content", command=self.analyze_content).pack(pady=5)
    
    def update_system_metrics(self):
        """Update system metrics display"""
        try:
            # Update CPU info
            cpu_info = self.system_monitor.get_cpu_info()
            if 'error' not in cpu_info:
                self.cpu_label.config(text=f"{cpu_info['usage_percent']:.1f}%")
            
            # Update Memory info
            memory_info = self.system_monitor.get_memory_info()
            if 'error' not in memory_info:
                self.memory_label.config(text=f"{memory_info['usage_percent']:.1f}% ({memory_info['used_gb']:.1f}GB/{memory_info['total_gb']:.1f}GB)")
            
            # Update Disk info
            disk_info = self.system_monitor.get_disk_info()
            if disk_info and 'error' not in disk_info[0]:
                main_disk = disk_info[0]
                self.disk_label.config(text=f"{main_disk['usage_percent']:.1f}% ({main_disk['used_gb']:.1f}GB/{main_disk['total_gb']:.1f}GB)")
            
            # Update process list
            processes = self.system_monitor.get_running_processes()
            self.process_tree.delete(*self.process_tree.get_children())
            
            for proc in processes[:10]:  # Show top 10
                self.process_tree.insert('', 'end', values=(
                    proc.get('name', 'Unknown'),
                    f"{proc.get('cpu_percent', 0):.1f}%",
                    f"{proc.get('memory_percent', 0):.1f}%",
                    proc.get('status', 'Unknown')
                ))
                
        except Exception as e:
            print(f"Error updating metrics: {e}")
    
    def start_monitoring(self):
        """Start system monitoring in background thread"""
        def monitor_loop():
            while True:
                try:
                    self.root.after(0, self.update_system_metrics)
                    time.sleep(3)  # Update every 3 seconds
                except Exception as e:
                    print(f"Monitoring error: {e}")
                    time.sleep(5)
        
        self.monitoring_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitoring_thread.start()
    
    def check_updates(self):
        """Check for system updates"""
        updates = self.system_optimizer.check_software_updates()
        self.optimize_text.delete('1.0', tk.END)
        self.optimize_text.insert(tk.END, f"Update Check Results:\n{'='*50}\n\n")
        self.optimize_text.insert(tk.END, json.dumps(updates, indent=2))
    
    def clean_cache(self):
        """Clean browser cache"""
        result = self.system_optimizer.cleanup_browser_cache()
        self.optimize_text.delete('1.0', tk.END)
        self.optimize_text.insert(tk.END, f"Browser Cache Cleanup Results:\n{'='*50}\n\n")
        self.optimize_text.insert(tk.END, json.dumps(result, indent=2))
    
    def analyze_startup(self):
        """Analyze startup programs"""
        startup = self.system_optimizer.analyze_startup_programs()
        self.optimize_text.delete('1.0', tk.END)
        self.optimize_text.insert(tk.END, f"Startup Programs Analysis:\n{'='*50}\n\n")
        for program in startup:
            if 'error' not in program:
                self.optimize_text.insert(tk.END, f"• {program['name']}\n")
                self.optimize_text.insert(tk.END, f"  Command: {program['command']}\n")
                self.optimize_text.insert(tk.END, f"  Source: {program['source']}\n\n")
    
    def disk_cleanup(self):
        """Perform disk cleanup"""
        self.optimize_text.delete('1.0', tk.END)
        self.optimize_text.insert(tk.END, f"Disk Cleanup:\n{'='*50}\n\n")
        
        # Get disk information
        disk_info = self.system_monitor.get_disk_info()
        for disk in disk_info:
            if 'error' not in disk:
                self.optimize_text.insert(tk.END, f"Drive: {disk['device']} ({disk['mountpoint']})\n")
                self.optimize_text.insert(tk.END, f"Usage: {disk['usage_percent']:.1f}%\n")
                self.optimize_text.insert(tk.END, f"Free Space: {disk['free_gb']:.1f} GB\n\n")
        
        self.optimize_text.insert(tk.END, "Cleanup suggestions:\n")
        self.optimize_text.insert(tk.END, "• Empty recycle bin\n")
        self.optimize_text.insert(tk.END, "• Clear temporary files\n")
        self.optimize_text.insert(tk.END, "• Remove unused applications\n")
        self.optimize_text.insert(tk.END, "• Compress old files\n")
    
    def perform_search(self):
        """Perform web search"""
        query = self.search_entry.get()
        if not query:
            messagebox.showwarning("Warning", "Please enter a search query")
            return
        
        results = self.web_assistant.web_search(query)
        self.web_text.delete('1.0', tk.END)
        self.web_text.insert(tk.END, f"Search Results for: {query}\n{'='*50}\n\n")
        
        if 'error' not in results:
            for result in results.get('results', []):
                self.web_text.insert(tk.END, f"Title: {result['title']}\n")
                self.web_text.insert(tk.END, f"URL: {result['url']}\n")
                self.web_text.insert(tk.END, f"Snippet: {result['snippet']}\n")
                self.web_text.insert(tk.END, "-" * 40 + "\n\n")
        else:
            self.web_text.insert(tk.END, f"Error: {results['error']}")
    
    def create_document(self):
        """Create a new document"""
        title = self.doc_title_entry.get()
        if not title:
            messagebox.showwarning("Warning", "Please enter a document title")
            return
        
        doc_type = self.doc_type_combo.get()
        document = self.writing_assistant.create_document(title, doc_type)
        
        if 'error' not in document:
            self.writing_text.delete('1.0', tk.END)
            self.writing_text.insert(tk.END, f"Document Created: {title}\n")
            self.writing_text.insert(tk.END, f"Type: {doc_type}\n")
            self.writing_text.insert(tk.END, f"ID: {document['id']}\n")
            self.writing_text.insert(tk.END, f"Created: {document['created_at']}\n\n")
            self.writing_text.insert(tk.END, "Start writing your content here...\n")
    
    def analyze_content(self):
        """Analyze writing content"""
        content = self.writing_text.get('1.0', tk.END).strip()
        if not content:
            messagebox.showwarning("Warning", "No content to analyze")
            return
        
        analysis = self.writing_assistant.analyze_content(content)
        
        analysis_window = tk.Toplevel(self.root)
        analysis_window.title("Content Analysis")
        analysis_window.geometry("400x300")
        
        text_widget = scrolledtext.ScrolledText(analysis_window, width=50, height=15)
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        text_widget.insert(tk.END, "Content Analysis:\n" + "="*30 + "\n\n")
        text_widget.insert(tk.END, f"Word Count: {analysis.get('word_count', 0)}\n")
        text_widget.insert(tk.END, f"Character Count: {analysis.get('character_count', 0)}\n")
        text_widget.insert(tk.END, f"Sentence Count: {analysis.get('sentence_count', 0)}\n")
        text_widget.insert(tk.END, f"Paragraph Count: {analysis.get('paragraph_count', 0)}\n")
        text_widget.insert(tk.END, f"Reading Time: ~{analysis.get('reading_time_minutes', 0)} minutes\n")
        text_widget.insert(tk.END, f"Words per Sentence: {analysis.get('avg_words_per_sentence', 0)}\n")
    
    def run(self):
        """Run the application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("Application terminated by user")
        except Exception as e:
            print(f"Application error: {e}")

def main():
    """Main entry point"""
    try:
        # Check system requirements
        if sys.version_info < (3, 7):
            print("Error: Python 3.7 or higher is required")
            return
        
        # Create and run the AI Desktop Assistant
        app = AIDesktopAssistant()
        app.run()
        
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install required packages:")
        print("pip install psutil requests")
    except Exception as e:
        print(f"Error starting application: {e}")

if __name__ == "__main__":
    main()