"""
Advanced System Optimization Module
Provides deep system cleaning and performance tuning capabilities
"""

import os
import shutil
import tempfile
import subprocess
import json
import platform
from pathlib import Path
from datetime import datetime, timedelta
import threading
import time

class AdvancedOptimizer:
    """Advanced system optimization and maintenance tools"""
    
    def __init__(self, config_file='config.json'):
        self.config = self.load_config(config_file)
        self.optimization_log = []
        self.safe_mode = True  # Enable safe operations by default
        
    def load_config(self, config_file):
        """Load configuration from file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except:
            return {
                "optimization": {
                    "auto_cleanup_interval": 7,
                    "cache_retention_days": 30,
                    "enable_auto_updates": False
                }
            }
    
    def deep_disk_cleanup(self) -> dict:
        """Perform comprehensive disk cleanup"""
        cleanup_results = {
            'items_cleaned': [],
            'space_freed_mb': 0,
            'errors': [],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            platform_system = platform.system()
            
            # Clean temporary files
            temp_cleaned = self.clean_temp_files()
            cleanup_results['items_cleaned'].extend(temp_cleaned['items'])
            cleanup_results['space_freed_mb'] += temp_cleaned['space_freed_mb']
            
            # Clean browser caches
            browser_cleaned = self.clean_all_browser_caches()
            cleanup_results['items_cleaned'].extend(browser_cleaned['items'])
            cleanup_results['space_freed_mb'] += browser_cleaned['space_freed_mb']
            
            # Clean system-specific junk
            if platform_system == "Windows":
                windows_cleaned = self.clean_windows_junk()
                cleanup_results['items_cleaned'].extend(windows_cleaned['items'])
                cleanup_results['space_freed_mb'] += windows_cleaned['space_freed_mb']
            elif platform_system == "Linux":
                linux_cleaned = self.clean_linux_junk()
                cleanup_results['items_cleaned'].extend(linux_cleaned['items'])
                cleanup_results['space_freed_mb'] += linux_cleaned['space_freed_mb']
            
            # Clean old downloads
            downloads_cleaned = self.clean_old_downloads()
            cleanup_results['items_cleaned'].extend(downloads_cleaned['items'])
            cleanup_results['space_freed_mb'] += downloads_cleaned['space_freed_mb']
            
        except Exception as e:
            cleanup_results['errors'].append(str(e))
        
        self.optimization_log.append(cleanup_results)
        return cleanup_results
    
    def clean_temp_files(self) -> dict:
        """Clean temporary files from system"""
        temp_paths = [
            tempfile.gettempdir(),
            Path.home() / "tmp",
            Path.home() / ".cache" / "tmp"
        ]
        
        result = {'items': [], 'space_freed_mb': 0}
        retention_days = self.config.get('optimization', {}).get('cache_retention_days', 30)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        for temp_path in temp_paths:
            if temp_path.exists():
                try:
                    for item in temp_path.iterdir():
                        try:
                            if item.stat().st_mtime < cutoff_date.timestamp():
                                size_mb = self.get_size_mb(item)
                                if item.is_file():
                                    item.unlink()
                                elif item.is_dir():
                                    shutil.rmtree(item)
                                
                                result['items'].append(str(item))
                                result['space_freed_mb'] += size_mb
                        except (PermissionError, OSError):
                            continue
                except (PermissionError, OSError):
                    continue
        
        return result
    
    def clean_all_browser_caches(self) -> dict:
        """Clean caches from all major browsers"""
        browsers = self.get_browser_cache_paths()
        result = {'items': [], 'space_freed_mb': 0}
        
        for browser_name, cache_paths in browsers.items():
            for cache_path in cache_paths:
                if cache_path.exists():
                    try:
                        size_before = self.get_directory_size_mb(cache_path)
                        shutil.rmtree(cache_path)
                        cache_path.mkdir(exist_ok=True)
                        result['items'].append(f"{browser_name}: {cache_path}")
                        result['space_freed_mb'] += size_before
                    except (PermissionError, OSError):
                        continue
        
        return result
    
    def get_browser_cache_paths(self):
        """Get cache paths for all major browsers"""
        home = Path.home()
        platform_system = platform.system()
        
        browsers = {
            'Chrome': [],
            'Firefox': [],
            'Edge': [],
            'Safari': []
        }
        
        if platform_system == "Windows":
            browsers['Chrome'] = [
                home / "AppData/Local/Google/Chrome/User Data/Default/Cache",
                home / "AppData/Local/Google/Chrome/User Data/Default/Code Cache"
            ]
            browsers['Firefox'] = [
                home / "AppData/Local/Mozilla/Firefox/Profiles"
            ]
            browsers['Edge'] = [
                home / "AppData/Local/Microsoft/Edge/User Data/Default/Cache"
            ]
        
        elif platform_system == "Linux":
            browsers['Chrome'] = [
                home / ".cache/google-chrome/Default/Cache",
                home / ".cache/google-chrome/Default/Code Cache"
            ]
            browsers['Firefox'] = [
                home / ".cache/mozilla/firefox"
            ]
        
        elif platform_system == "Darwin":  # macOS
            browsers['Chrome'] = [
                home / "Library/Caches/Google/Chrome/Default/Cache",
                home / "Library/Caches/Google/Chrome/Default/Code Cache"
            ]
            browsers['Firefox'] = [
                home / "Library/Caches/Firefox/Profiles"
            ]
            browsers['Safari'] = [
                home / "Library/Caches/com.apple.Safari"
            ]
        
        return browsers
    
    def clean_windows_junk(self) -> dict:
        """Clean Windows-specific junk files"""
        result = {'items': [], 'space_freed_mb': 0}
        
        if platform.system() != "Windows":
            return result
        
        # Clean Windows temp folders
        windows_temp = Path("C:/Windows/Temp")
        prefetch = Path("C:/Windows/Prefetch")
        
        junk_paths = [windows_temp, prefetch]
        
        for junk_path in junk_paths:
            if junk_path.exists():
                try:
                    size_before = self.get_directory_size_mb(junk_path)
                    for item in junk_path.iterdir():
                        try:
                            if item.is_file():
                                item.unlink()
                            elif item.is_dir():
                                shutil.rmtree(item)
                        except (PermissionError, OSError):
                            continue
                    result['items'].append(str(junk_path))
                    result['space_freed_mb'] += size_before
                except (PermissionError, OSError):
                    continue
        
        # Run Windows built-in disk cleanup
        try:
            subprocess.run(['cleanmgr', '/sagerun:1'], check=False)
            result['items'].append("Windows Disk Cleanup initiated")
        except:
            pass
        
        return result
    
    def clean_linux_junk(self) -> dict:
        """Clean Linux-specific junk files"""
        result = {'items': [], 'space_freed_mb': 0}
        
        if platform.system() != "Linux":
            return result
        
        # Clean package cache
        try:
            # apt cache cleanup
            subprocess.run(['sudo', 'apt', 'clean'], check=False)
            result['items'].append("APT package cache cleaned")
            
            # Remove orphaned packages
            subprocess.run(['sudo', 'apt', 'autoremove', '-y'], check=False)
            result['items'].append("Orphaned packages removed")
            
        except:
            pass
        
        # Clean journal logs
        try:
            subprocess.run(['sudo', 'journalctl', '--vacuum-time=7d'], check=False)
            result['items'].append("System journal logs cleaned (last 7 days)")
        except:
            pass
        
        return result
    
    def clean_old_downloads(self) -> dict:
        """Clean old files from Downloads folder"""
        result = {'items': [], 'space_freed_mb': 0}
        downloads_path = Path.home() / "Downloads"
        
        if not downloads_path.exists():
            return result
        
        retention_days = self.config.get('optimization', {}).get('cache_retention_days', 30)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        try:
            for item in downloads_path.iterdir():
                if item.stat().st_mtime < cutoff_date.timestamp():
                    try:
                        size_mb = self.get_size_mb(item)
                        if item.is_file():
                            # Don't delete important file types
                            if not item.suffix.lower() in ['.exe', '.msi', '.dmg', '.pkg']:
                                item.unlink()
                                result['items'].append(str(item))
                                result['space_freed_mb'] += size_mb
                        elif item.is_dir():
                            # Be careful with directories
                            if not any(keyword in item.name.lower() for keyword in ['important', 'work', 'documents']):
                                shutil.rmtree(item)
                                result['items'].append(f"Directory: {item}")
                                result['space_freed_mb'] += size_mb
                    except (PermissionError, OSError):
                        continue
        except (PermissionError, OSError):
            pass
        
        return result
    
    def optimize_startup_programs(self) -> dict:
        """Analyze and optimize startup programs"""
        result = {
            'startup_items': [],
            'recommendations': [],
            'can_disable': [],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            platform_system = platform.system()
            
            if platform_system == "Windows":
                import winreg
                
                # Check user startup registry entries
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
                                startup_item = {
                                    'name': name,
                                    'command': value,
                                    'location': f"Registry: {key_path}",
                                    'user_specific': True
                                }
                                result['startup_items'].append(startup_item)
                                
                                # Provide recommendations
                                if self.should_disable_startup(name, value):
                                    result['can_disable'].append(name)
                                    result['recommendations'].append(f"Consider disabling: {name}")
                                
                                i += 1
                    except WindowsError:
                        break
                
                # Check startup folder
                startup_folder = Path.home() / "AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup"
                if startup_folder.exists():
                    for item in startup_folder.iterdir():
                        startup_item = {
                            'name': item.name,
                            'command': str(item),
                            'location': f"Startup Folder: {startup_folder}",
                            'user_specific': True
                        }
                        result['startup_items'].append(startup_item)
            
            elif platform_system == "Linux":
                # Check systemd services
                try:
                    output = subprocess.run(['systemctl', 'list-unit-files', '--state=enabled', '--type=service'], 
                                          capture_output=True, text=True)
                    if output.returncode == 0:
                        for line in output.stdout.split('\n'):
                            if 'service' in line and 'enabled' in line:
                                service_name = line.split('.')[0].strip()
                                startup_item = {
                                    'name': service_name,
                                    'command': f'systemctl start {service_name}',
                                    'location': 'systemd',
                                    'user_specific': False
                                }
                                result['startup_items'].append(startup_item)
                except:
                    pass
        
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def should_disable_startup(self, name: str, command: str) -> bool:
        """Determine if a startup program can be safely disabled"""
        safe_to_disable = [
            'update', 'helper', 'monitor', 'notification', 'sync',
            'backup', 'updater', 'launcher', 'quickstart'
        ]
        
        essential = [
            'security', 'antivirus', 'firewall', 'vpn', 'defender',
            'windows', 'system', 'critical'
        ]
        
        name_lower = name.lower()
        command_lower = command.lower()
        
        # Don't disable essential programs
        if any(keyword in name_lower or keyword in command_lower for keyword in essential):
            return False
        
        # Consider disabling programs with certain keywords
        if any(keyword in name_lower or keyword in command_lower for keyword in safe_to_disable):
            return True
        
        return False
    
    def optimize_power_settings(self) -> dict:
        """Optimize system power settings for performance"""
        result = {
            'changes_made': [],
            'recommendations': [],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            platform_system = platform.system()
            
            if platform_system == "Windows":
                # Set power plan to High Performance
                try:
                    subprocess.run(['powercfg', '/setactive', 'SCHEME_MIN'], check=False)
                    result['changes_made'].append("Power plan set to High Performance")
                except:
                    result['recommendations'].append("Manually set power plan to High Performance")
                
                # Disable sleep mode
                try:
                    subprocess.run(['powercfg', '/change', 'standby-timeout-ac', '0'], check=False)
                    subprocess.run(['powercfg', '/change', 'standby-timeout-dc', '0'], check=False)
                    result['changes_made'].append("Sleep mode disabled")
                except:
                    pass
            
            elif platform_system == "Linux":
                # Check CPU governor
                try:
                    with open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor', 'r') as f:
                        governor = f.read().strip()
                    
                    if governor != 'performance':
                        result['recommendations'].append("Consider setting CPU governor to 'performance' mode")
                        result['recommendations'].append("Run: sudo cpupower frequency-set -g performance")
                except:
                    pass
        
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def disable_visual_effects(self) -> dict:
        """Disable visual effects for better performance"""
        result = {
            'changes_made': [],
            'recommendations': [],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            platform_system = platform.system()
            
            if platform_system == "Windows":
                # Disable visual effects through registry
                import winreg
                
                visual_effects_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects"
                
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, visual_effects_key, 0, winreg.KEY_SET_VALUE) as key:
                        winreg.SetValueEx(key, "VisualFXSetting", 0, winreg.REG_DWORD, 2)  # Custom
                        winreg.SetValueEx(key, "MaxAnimate", 0, winreg.REG_DWORD, 0)  # Disable animations
                        
                    result['changes_made'].append("Visual effects optimized for performance")
                except:
                    result['recommendations'].append("Manually disable visual effects in System Properties")
            
            elif platform_system == "Linux":
                # Check desktop environment and provide recommendations
                desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
                
                if 'gnome' in desktop:
                    result['recommendations'].append("Disable GNOME animations using GNOME Tweaks")
                    result['recommendations'].append("Set 'Animations' to 'Off' in GNOME Tweaks")
                elif 'kde' in desktop:
                    result['recommendations'].append("Disable KDE desktop effects in System Settings")
        
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def optimize_network_settings(self) -> dict:
        """Optimize network settings for better performance"""
        result = {
            'changes_made': [],
            'recommendations': [],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            platform_system = platform.system()
            
            if platform_system == "Windows":
                # Optimize TCP settings
                try:
                    subprocess.run(['netsh', 'int', 'tcp', 'set', 'global', 'autotuninglevel=highlyrestricted'], check=False)
                    result['changes_made'].append("TCP auto-tuning optimized")
                except:
                    pass
                
                # Disable Nagle's algorithm for gaming
                try:
                    subprocess.run(['reg', 'add', 'HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters', 
                                  '/v', 'TcpAckFrequency', '/t', 'REG_DWORD', '/d', '1', '/f'], check=False)
                    subprocess.run(['reg', 'add', 'HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters', 
                                  '/v', 'TCPNoDelay', '/t', 'REG_DWORD', '/d', '1', '/f'], check=False)
                    result['changes_made'].append("Network latency optimized")
                except:
                    pass
            
            # General recommendations
            result['recommendations'].extend([
                "Use wired Ethernet connection when possible",
                "Disable unused network adapters",
                "Update network adapter drivers",
                "Disable background syncing (OneDrive, Dropbox, etc.) when not needed"
            ])
        
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def get_size_mb(self, path) -> float:
        """Get size of a file or directory in MB"""
        try:
            if path.is_file():
                return round(path.stat().st_size / (1024 * 1024), 2)
            elif path.is_dir():
                return self.get_directory_size_mb(path)
        except:
            pass
        return 0
    
    def get_directory_size_mb(self, directory) -> float:
        """Get total size of directory in MB"""
        total_size = 0
        try:
            for item in directory.rglob('*'):
                if item.is_file():
                    try:
                        total_size += item.stat().st_size
                    except:
                        continue
        except:
            pass
        return round(total_size / (1024 * 1024), 2)
    
    def generate_optimization_report(self) -> dict:
        """Generate comprehensive optimization report"""
        report = {
            'system_info': self.get_system_info(),
            'optimization_history': self.optimization_log[-10:],  # Last 10 optimizations
            'recommendations': self.get_system_recommendations(),
            'generated_at': datetime.now().isoformat()
        }
        
        return report
    
    def get_system_info(self) -> dict:
        """Get basic system information"""
        import psutil
        
        return {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
            'cpu_count': psutil.cpu_count(),
            'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
            'disk_info': self.get_disk_summary()
        }
    
    def get_disk_summary(self) -> list:
        """Get summary of disk usage"""
        import psutil
        
        disks = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'total_gb': round(usage.total / (1024**3), 2),
                    'used_gb': round(usage.used / (1024**3), 2),
                    'free_gb': round(usage.free / (1024**3), 2),
                    'usage_percent': round((usage.used / usage.total) * 100, 2)
                })
            except:
                continue
        return disks
    
    def get_system_recommendations(self) -> list:
        """Get system-specific optimization recommendations"""
        recommendations = []
        
        # General recommendations
        recommendations.extend([
            "Regularly restart your system to clear memory",
            "Keep your operating system and drivers updated",
            "Use lightweight antivirus software",
            "Avoid running too many browser tabs simultaneously",
            "Consider upgrading to SSD if still using HDD"
        ])
        
        # Platform-specific recommendations
        if platform.system() == "Windows":
            recommendations.extend([
                "Disable Windows Search indexing for better performance",
                "Turn off Cortana if not used",
                "Disable unnecessary startup programs",
                "Use Game Mode when gaming"
            ])
        elif platform.system() == "Linux":
            recommendations.extend([
                "Use a lightweight desktop environment",
                "Disable unnecessary system services",
                "Consider using Btrfs or ext4 file systems",
                "Keep your package manager cache clean"
            ])
        
        return recommendations