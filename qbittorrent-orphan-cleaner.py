#!/usr/bin/env python3
"""
qBittorrent Orphaned Files Cleaner
==================================
This script identifies and optionally removes files that are no longer associated 
with any active torrents in qBittorrent.

Author: UgaBugaB00
License: MIT
"""

import os
import sys
import getpass
from pathlib import Path

# Check for required packages
try:
    import qbittorrentapi
except ImportError:
    print("ERROR: qbittorrent-api package is not installed.")
    print("\nTo install it, run one of the following commands:")
    print("  pip install qbittorrent-api")
    print("  pip3 install qbittorrent-api")
    print("  python -m pip install qbittorrent-api")
    print("\nIf you're on Debian/Ubuntu, you might need to install pip first:")
    print("  sudo apt-get update")
    print("  sudo apt-get install python3-pip")
    sys.exit(1)

def format_bytes(size):
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"

def get_connection_info():
    """Interactively get connection information from user"""
    print("="*60)
    print("qBittorrent Connection Setup")
    print("="*60)
    
    # Get host
    host = input("Enter qBittorrent host IP/hostname (default: localhost): ").strip()
    if not host:
        host = "localhost"
    
    # Get port
    while True:
        port_str = input("Enter qBittorrent WebUI port (default: 8080): ").strip()
        if not port_str:
            port = 8080
            break
        try:
            port = int(port_str)
            if 1 <= port <= 65535:
                break
            else:
                print("Port must be between 1 and 65535")
        except ValueError:
            print("Invalid port number. Please enter a number.")
    
    # Get username
    username = input("Enter qBittorrent username: ").strip()
    while not username:
        print("Username cannot be empty!")
        username = input("Enter qBittorrent username: ").strip()
    
    # Get password (hidden input)
    password = getpass.getpass("Enter qBittorrent password: ")
    while not password:
        print("Password cannot be empty!")
        password = getpass.getpass("Enter qBittorrent password: ")
    
    # Get download path
    while True:
        download_dir = input("Enter download directory path: ").strip()
        if not download_dir:
            print("Download directory cannot be empty!")
            continue
        
        # Expand user home directory if used
        download_dir = os.path.expanduser(download_dir)
        
        if not os.path.exists(download_dir):
            print(f"Warning: Directory '{download_dir}' does not exist!")
            create = input("Do you want to continue anyway? (yes/no): ").lower()
            if create == 'yes':
                break
        elif not os.path.isdir(download_dir):
            print(f"Error: '{download_dir}' is not a directory!")
        else:
            break
    
    # Ensure trailing slash for consistency
    if not download_dir.endswith('/'):
        download_dir += '/'
    
    return host, port, username, password, download_dir

def test_connection(conn_info):
    """Test the connection to qBittorrent"""
    print("\nTesting connection to qBittorrent...")
    
    try:
        qbt_client = qbittorrentapi.Client(**conn_info)
        qbt_client.auth_log_in()
        print("✓ Successfully connected to qBittorrent")
        return qbt_client
    except qbittorrentapi.LoginFailed:
        print("\nERROR: Login failed!")
        print("Possible causes:")
        print("  1. Incorrect username or password")
        print("  2. WebUI authentication is not enabled")
        print("  3. IP is banned due to too many failed login attempts")
        print("\nTo check WebUI settings:")
        print("  1. Access qBittorrent directly")
        print("  2. Go to Tools → Options → Web UI")
        print("  3. Ensure 'Web User Interface' is enabled")
        print("  4. Check username and password settings")
        return None
    except qbittorrentapi.APIConnectionError as e:
        print(f"\nERROR: Cannot connect to qBittorrent at {conn_info['host']}:{conn_info['port']}")
        print("\nPossible causes:")
        print("  1. qBittorrent is not running")
        print("  2. WebUI is not enabled")
        print("  3. Wrong IP address or port")
        print("  4. Firewall is blocking the connection")
        print("\nTo check if qBittorrent is running:")
        print("  systemctl status qbittorrent-nox")
        print("  # or")
        print("  ps aux | grep qbittorrent")
        print("\nTo check what port qBittorrent is using:")
        print("  sudo netstat -tlnp | grep qbittorrent")
        return None
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        return None

def scan_torrents(qbt_client, download_dir):
    """Scan all active torrents and find orphaned files"""
    active_files = set()
    active_dirs = set()
    
    print("\nScanning active torrents...")
    try:
        torrents = qbt_client.torrents_info()
        torrent_count = len(torrents)
        
        for i, torrent in enumerate(torrents):
            print(f"\rProcessing torrent {i+1}/{torrent_count}...", end='', flush=True)
            
            # Get the save path for this torrent
            save_path = torrent.save_path
            
            # Get all files for this torrent
            try:
                torrent_files = torrent.files
                for file in torrent_files:
                    file_path = os.path.join(save_path, file.name)
                    active_files.add(file_path)
                    
                    # Track parent directories
                    parent = os.path.dirname(file_path)
                    while parent and parent != save_path:
                        active_dirs.add(parent)
                        parent = os.path.dirname(parent)
            except Exception as e:
                print(f"\nWarning: Could not get files for torrent '{torrent.name}': {e}")
        
        print(f"\n✓ Found {torrent_count} active torrents with {len(active_files)} files")
        
    except Exception as e:
        print(f"\nERROR: Failed to retrieve torrent information: {e}")
        return None, None
    
    # Find orphaned files
    orphaned_files = []
    total_orphaned_size = 0
    
    print(f"\nScanning directory: {download_dir}")
    
    if not os.path.exists(download_dir):
        print(f"ERROR: Directory '{download_dir}' does not exist!")
        return orphaned_files, total_orphaned_size
    
    try:
        file_count = 0
        for root, dirs, files in os.walk(download_dir):
            for file in files:
                file_count += 1
                if file_count % 100 == 0:
                    print(f"\rScanning files: {file_count}...", end='', flush=True)
                
                full_path = os.path.join(root, file)
                if full_path not in active_files:
                    try:
                        file_size = os.path.getsize(full_path)
                        orphaned_files.append((full_path, file_size))
                        total_orphaned_size += file_size
                    except OSError as e:
                        # File might have been deleted or inaccessible
                        print(f"\nWarning: Cannot access file '{full_path}': {e}")
                        orphaned_files.append((full_path, 0))
        
        print(f"\r✓ Scanned {file_count} files total")
        
    except PermissionError as e:
        print(f"\nERROR: Permission denied while scanning directory: {e}")
        print("Try running the script with sudo or check directory permissions")
        return None, None
    except Exception as e:
        print(f"\nERROR: Failed to scan directory: {e}")
        return None, None
    
    return orphaned_files, total_orphaned_size

def main():
    """Main function"""
    print("="*60)
    print("qBittorrent Orphaned Files Cleaner v1.0")
    print("="*60)
    print("\nThis script will help you find and remove files that are")
    print("no longer associated with any active torrents.\n")
    
    # Get connection information
    host, port, username, password, download_dir = get_connection_info()
    
    conn_info = dict(
        host=host,
        port=port,
        username=username,
        password=password,
    )
    
    # Test connection
    qbt_client = test_connection(conn_info)
    if not qbt_client:
        print("\nFailed to connect to qBittorrent. Please check your settings and try again.")
        sys.exit(1)
    
    # Scan for orphaned files
    orphaned_files, total_orphaned_size = scan_torrents(qbt_client, download_dir)
    
    if orphaned_files is None:
        print("\nScript encountered an error. Please check the messages above.")
        qbt_client.auth_log_out()
        sys.exit(1)
    
    # Sort by size (largest first)
    orphaned_files.sort(key=lambda x: x[1], reverse=True)
    
    # Display results
    print("\n" + "="*60)
    print("ORPHANED FILES REPORT")
    print("="*60)
    print(f"Total orphaned files: {len(orphaned_files)}")
    print(f"Total size: {format_bytes(total_orphaned_size)}")
    print("="*60)
    
    if orphaned_files:
        print("\nTop 20 largest orphaned files:")
        for i, (file_path, size) in enumerate(orphaned_files[:20]):
            # Show relative path for readability
            display_path = file_path.replace(download_dir, '')
            print(f"{i+1:3d}. {format_bytes(size):>10} - {display_path}")
        
        if len(orphaned_files) > 20:
            print(f"\n... and {len(orphaned_files) - 20} more files")
        
        # Save full list to file
        output_file = os.path.expanduser("~/qbittorrent_orphaned_files.txt")
        try:
            with open(output_file, 'w') as f:
                f.write(f"Orphaned Files Report\n")
                f.write(f"Generated by: qBittorrent Orphaned Files Cleaner\n")
                f.write(f"Download Directory: {download_dir}\n")
                f.write(f"Total files: {len(orphaned_files)}\n")
                f.write(f"Total size: {format_bytes(total_orphaned_size)}\n")
                f.write("="*60 + "\n\n")
                for file_path, size in orphaned_files:
                    display_path = file_path.replace(download_dir, '')
                    f.write(f"{format_bytes(size):>10} - {display_path}\n")
            print(f"\n✓ Full list saved to: {output_file}")
        except Exception as e:
            print(f"\nWarning: Could not save report file: {e}")
        
        # Optional: Delete files
        print("\n" + "="*60)
        response = input("\nDo you want to delete these orphaned files? (yes/no): ").lower().strip()
        if response == 'yes':
            confirm = input(f"\nThis will delete {len(orphaned_files)} files ({format_bytes(total_orphaned_size)}).\nType 'DELETE' to confirm: ")
            if confirm == 'DELETE':
                deleted_count = 0
                deleted_size = 0
                failed_count = 0
                
                print("\nDeleting files...")
                for file_path, size in orphaned_files:
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                        deleted_size += size
                        if deleted_count % 10 == 0:
                            print(f"\rDeleted {deleted_count}/{len(orphaned_files)} files...", end='', flush=True)
                    except Exception as e:
                        failed_count += 1
                        print(f"\nError deleting {file_path}: {e}")
                
                print(f"\n\n✓ Deleted {deleted_count} files, freed {format_bytes(deleted_size)}")
                if failed_count > 0:
                    print(f"⚠ Failed to delete {failed_count} files (check permissions)")
            else:
                print("Deletion cancelled")
    else:
        print("\n✓ No orphaned files found! Your download directory is clean.")
    
    # Logout
    try:
        qbt_client.auth_log_out()
    except:
        pass
    
    print("\nDone!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nScript interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        print("Please report this issue on GitHub with the full error message.")
        sys.exit(1)