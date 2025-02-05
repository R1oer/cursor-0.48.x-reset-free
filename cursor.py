import os
import sys
import json
import uuid
import time
import ctypes
import winreg
import shutil
import random
import psutil
import datetime
import itertools
import threading
from pathlib import Path
from typing import Optional

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    PURPLE = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    NC = '\033[0m'

class Paths:
    """Application paths configuration"""
    APPDATA = os.getenv('APPDATA')
    STORAGE_FILE = os.path.join(APPDATA, 'Cursor', 'User', 'globalStorage', 'storage.json')
    BACKUP_DIR = os.path.join(APPDATA, 'Cursor', 'User', 'globalStorage', 'backups')

class Spinner:
    def __init__(self):
        self.spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        self.running = False
        self.spinner_thread = None

    def spin(self, text: str):
        while self.running:
            sys.stdout.write(f'\r{Colors.CYAN}{next(self.spinner)}{Colors.NC} {text}')
            sys.stdout.flush()
            time.sleep(0.1)

    def start(self, text: str):
        self.running = True
        self.spinner_thread = threading.Thread(target=self.spin, args=(text,))
        self.spinner_thread.start()

    def stop(self):
        self.running = False
        if self.spinner_thread:
            self.spinner_thread.join()
        sys.stdout.write('\r')
        sys.stdout.flush()

spinner = Spinner()

def is_admin() -> bool:
    """Check if the script is running with administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def log_info(msg: str) -> None:
    """Log information message"""
    print(f"{Colors.GREEN}[•]{Colors.NC} {msg}")

def log_warn(msg: str) -> None:
    """Log warning message"""
    print(f"{Colors.YELLOW}[!]{Colors.NC} {msg}")

def log_error(msg: str) -> None:
    """Log error message"""
    print(f"{Colors.RED}[×]{Colors.NC} {msg}")

def log_debug(msg: str) -> None:
    """Log debug message"""
    print(f"{Colors.BLUE}[*]{Colors.NC} {msg}")

def print_logo() -> None:
    """Display application logo and information"""
    frames = [
        f'''{Colors.CYAN}
    ██████╗██╗   ██╗██████╗ ███████╗ ██████╗ ██████╗ 
   ██╔════╝██║   ██║██╔══██╗██╔════╝██╔═══██╗██╔══██╗
   ██║     ██║   ██║██████╔╝███████╗██║   ██║██████╔╝
   ██║     ██║   ██║██╔══██╗╚════██║██║   ██║██╔══██╗
   ╚██████╗╚██████╔╝██║  ██║███████║╚██████╔╝██║  ██║
    ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝{Colors.NC}''',
        f'''{Colors.PURPLE}
    ██████╗██╗   ██╗██████╗ ███████╗ ██████╗ ██████╗ 
   ██╔════╝██║   ██║██╔══██╗██╔════╝██╔═══██╗██╔══██╗
   ██║     ██║   ██║██████╔╝███████╗██║   ██║██████╔╝
   ██║     ██║   ██║██╔══██╗╚════██║██║   ██║██╔══██╗
   ╚██████╗╚██████╔╝██║  ██║███████║╚██████╔╝██║  ██║
    ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝{Colors.NC}'''
    ]
    
    for _ in range(3):
        for frame in frames:
            print('\033[2J\033[H', end='')
            print(frame)
            print(f"\n{Colors.BLUE}═══════════════════════════════════════════{Colors.NC}")
            print(f"{Colors.GREEN}            Cursor ID Modifier              {Colors.NC}")
            print(f"{Colors.YELLOW}     Advanced Cursor Management Tool       {Colors.NC}")
            print(f"{Colors.BLUE}═══════════════════════════════════════════{Colors.NC}\n")
            time.sleep(0.3)

def get_cursor_version() -> Optional[str]:
    """Get installed Cursor version from package.json"""
    try:
        package_paths = [
            os.path.join(os.getenv('LOCALAPPDATA'), 'Programs', 'cursor', 'resources', 'app', 'package.json'),
            os.path.join(os.getenv('LOCALAPPDATA'), 'cursor', 'resources', 'app', 'package.json')
        ]
        
        spinner.start("Detecting Cursor version")
        time.sleep(1)
        
        for path in package_paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    version = data.get('version')
                    if version:
                        spinner.stop()
                        log_info(f"Detected Cursor v{version}")
                        return version
        
        spinner.stop()
        log_warn("Unable to detect Cursor version")
        log_warn("Please ensure Cursor is properly installed")
        return None
    except Exception as e:
        spinner.stop()
        log_error(f"Version detection failed: {e}")
        return None

def check_and_kill_cursor() -> None:
    """Check and terminate all running Cursor processes"""
    spinner.start("Checking for running Cursor processes")
    time.sleep(1)
    
    for _ in range(5):
        cursor_processes = [p for p in psutil.process_iter(['pid', 'name']) 
                          if 'cursor' in p.info['name'].lower()]
        
        if not cursor_processes:
            spinner.stop()
            return
            
        spinner.stop()
        log_warn("Found running Cursor processes")
        
        spinner.start("Terminating processes")
        for proc in cursor_processes:
            try:
                proc.terminate()
                proc.wait(timeout=1)
            except:
                try:
                    proc.kill()
                except:
                    spinner.stop()
                    log_error(f"Failed to terminate process {proc.info['pid']}")
        
        time.sleep(1)
    
    spinner.stop()
    if any(p for p in psutil.process_iter(['name']) if 'cursor' in p.info['name'].lower()):
        log_error("Unable to close all Cursor processes")
        log_warn("Please close Cursor manually and try again")
        sys.exit(1)

def backup_config() -> None:
    """Create backup of current configuration"""
    if not os.path.exists(Paths.STORAGE_FILE):
        log_warn("No configuration found to backup")
        return
    
    spinner.start("Creating backup")
    os.makedirs(Paths.BACKUP_DIR, exist_ok=True)
    backup_file = os.path.join(
        Paths.BACKUP_DIR, 
        f"storage.json.backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    
    try:
        shutil.copy2(Paths.STORAGE_FILE, backup_file)
        time.sleep(1)
        spinner.stop()
        log_info(f"Backup created: {backup_file}")
    except Exception as e:
        spinner.stop()
        log_error(f"Backup failed: {e}")
        sys.exit(1)

def generate_machine_id() -> str:
    """Generate new machine ID with specific format"""
    prefix = "auth0|user_"
    prefix_hex = prefix.encode('utf-8').hex()
    random_hex = ''.join(random.choices('0123456789abcdef', k=64))
    return f"{prefix_hex}{random_hex}"

def update_machine_guid() -> None:
    """Update system Machine GUID in registry"""
    try:
        spinner.start("Updating system Machine GUID")
        new_guid = str(uuid.uuid4())
        key_path = r"SOFTWARE\Microsoft\Cryptography"
        
        backup_file = os.path.join(
            Paths.BACKUP_DIR,
            f"MachineGuid.backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ) as key:
            current_guid = winreg.QueryValueEx(key, "MachineGuid")[0]
            with open(backup_file, 'w') as f:
                f.write(current_guid)
        
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "MachineGuid", 0, winreg.REG_SZ, new_guid)
        
        time.sleep(1)
        spinner.stop()
        log_info(f"System GUID updated successfully")
        log_debug(f"New GUID: {new_guid}")
        log_debug(f"Backup: {backup_file}")
        
    except Exception as e:
        spinner.stop()
        log_error(f"GUID update failed: {e}")

def generate_new_config() -> None:
    """Generate and update configuration with new identifiers"""
    if not os.path.exists(Paths.STORAGE_FILE):
        log_error(f"Configuration file not found")
        log_warn("Please run Cursor at least once before using this tool")
        sys.exit(1)
    
    try:
        spinner.start("Reading current configuration")
        with open(Paths.STORAGE_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        time.sleep(1)
        
        spinner.stop()
        spinner.start("Generating new identifiers")
        
        machine_id = generate_machine_id()
        mac_machine_id = str(uuid.uuid4()).replace('-', '')
        device_id = str(uuid.uuid4())
        sqm_id = "{" + str(uuid.uuid4()).upper() + "}"
        
        config['telemetry.machineId'] = machine_id
        config['telemetry.macMachineId'] = mac_machine_id
        config['telemetry.devDeviceId'] = device_id
        config['telemetry.sqmId'] = sqm_id
        
        time.sleep(1)
        spinner.stop()
        spinner.start("Saving new configuration")
        
        with open(Paths.STORAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        
        time.sleep(1)
        spinner.stop()
        
        log_info("Configuration updated successfully")
        log_debug(f"Machine ID: {machine_id}")
        log_debug(f"MAC ID: {mac_machine_id}")
        log_debug(f"Device ID: {device_id}")
        log_debug(f"SQM ID: {sqm_id}")
        
    except Exception as e:
        spinner.stop()
        log_error(f"Configuration update failed: {e}")
        sys.exit(1)

def disable_auto_update() -> None:
    """Disable Cursor auto-update functionality"""
    updater_path = os.path.join(os.getenv('LOCALAPPDATA'), 'cursor-updater')
    
    try:
        print()
        log_warn("Would you like to disable auto-updates?")
        print(f"{Colors.WHITE}0) No - keep auto-updates enabled (default)")
        print(f"1) Yes - disable auto-updates{Colors.NC}")
        
        choice = input(f"\n{Colors.CYAN}Select option (0):{Colors.NC} ").strip()
        
        if choice == "1":
            spinner.start("Disabling auto-updates")
            
            if os.path.exists(updater_path):
                if os.path.isfile(updater_path):
                    os.remove(updater_path)
                else:
                    shutil.rmtree(updater_path)
            
            with open(updater_path, 'w') as f:
                pass
            
            os.chmod(updater_path, 0o444)
            
            time.sleep(1)
            spinner.stop()
            log_info("Auto-updates disabled successfully")
            
        else:
            log_info("Auto-updates remain enabled")
            
    except Exception as e:
        spinner.stop()
        log_error(f"Failed to disable auto-updates: {e}")
        log_warn("Manual steps to disable:")
        print(f"{Colors.WHITE}1. Remove directory: {updater_path}")
        print("2. Create empty file with same name")
        print(f"3. Make file read-only{Colors.NC}")

def show_file_tree() -> None:
    """Display the file structure of the application"""
    base_dir = os.path.dirname(Paths.STORAGE_FILE)
    print()
    log_info("File Structure Overview:")
    print(f"{Colors.BLUE}{base_dir}{Colors.NC}")
    print(f"{Colors.WHITE}├── globalStorage")
    print("│   ├── storage.json (modified)")
    print(f"│   └── backups{Colors.NC}")
    
    if os.path.exists(Paths.BACKUP_DIR):
        backup_files = os.listdir(Paths.BACKUP_DIR)
        if backup_files:
            for file in backup_files:
                print(f"{Colors.WHITE}│       └── {file}{Colors.NC}")

def main():
    """Main application entry point"""
    print_logo()
    
    if not is_admin():
        log_error("Administrator privileges required")
        sys.exit(1)
    
    version = get_cursor_version()
    if not version:
        sys.exit(1)
    
    check_and_kill_cursor()
    backup_config()
    update_machine_guid()
    generate_new_config()
    disable_auto_update()
    show_file_tree()
    
    print()
    log_info("All operations completed successfully")
    print(f"\n{Colors.WHITE}Press Enter to exit...{Colors.NC}")
    input()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(0) 