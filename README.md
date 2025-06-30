# qBittorrent Orphaned Files Cleaner

A Python script to find and remove files that are no longer associated with any active torrents in qBittorrent. This helps you reclaim disk space by cleaning up leftover files from deleted torrents.

## Features

-   🔍 **Scans your download directory** for orphaned files and folders.
-   📊 **Shows total count and size** of all orphaned files found.
-   📝 **Generates a detailed report** (`orphaned_files.txt`) listing all files identified for deletion.
-   🗑️ **Optionally deletes** orphaned files and empty directories after your confirmation.
-   🛡️ **Safe by design** with multiple explicit confirmation steps before any deletion occurs.
-   💬 **Interactive setup** to guide you through connecting to qBittorrent and configuring the script.
-   ⚙️ **Handles complex scenarios**, including nested directories and partially downloaded files.

## Requirements

-   Python 3.6 or higher
-   qBittorrent with Web UI enabled
-   `qbittorrent-api` Python package

## Installation

#### Option 1: Git Clone (Recommended)

1.  **Clone this repository:**
    ```bash
    git clone [https://github.com/UgaBugaBoo/qbittorrent_orphan-cleaner.git](https://github.com/UgaBugaBoo/qbittorrent_orphan-cleaner.git)
    cd qbittorrent_orphan-cleaner
    ```

2.  **Install the required Python package:**
    ```bash
    pip install qbittorrent-api
    ```

3.  **Run the script:**
    ```bash
    python3 qbittorrent-orphan-cleaner.py
    ```

#### Option 2: Quick Run (No Git Required)

You can download and run the script directly without cloning the repository.

-   **Using `wget`:**
    ```bash
    wget [https://raw.githubusercontent.com/UgaBugaBoo/qbittorrent_orphan-cleaner/main/qbittorrent-orphan-cleaner.py](https://raw.githubusercontent.com/UgaBugaBoo/qbittorrent_orphan-cleaner/main/qbittorrent-orphan-cleaner.py)
    python3 qbittorrent-orphan-cleaner.py
    ```

-   **Using `curl`:**
    ```bash
    curl -O [https://raw.githubusercontent.com/UgaBugaBoo/qbittorrent_orphan-cleaner/main/qbittorrent-orphan-cleaner.py](https://raw.githubusercontent.com/UgaBugaBoo/qbittorrent_orphan-cleaner/main/qbittorrent-orphan-cleaner.py)
    python3 qbittorrent-orphan-cleaner.py
    ```
    *Note: You still need to install the required package: `pip install qbittorrent-api`*


## Usage

1.  **Run the script from your terminal:**
    ```bash
    python3 qbittorrent-orphan-cleaner.py
    ```

2.  The script will interactively prompt you for the following information:
    -   qBittorrent host/IP address (e.g., `localhost`, `192.168.1.10`)
    -   WebUI port number
    -   Your qBittorrent username and password
    -   The absolute path to your main download directory

The script will then scan the directory and present you with a summary of orphaned files. You will be asked for explicit confirmation before any files are deleted.

### Enabling qBittorrent Web UI

For the script to connect to qBittorrent, you must have the Web UI enabled.

1.  Open qBittorrent.
2.  Go to **Tools → Options → Web UI**.
3.  Check the box for **"Web User Interface (Remote control)"**.
4.  Set a secure **Username** and **Password**.
5.  Note the **Port** number (the default is usually `8080`).

---

## Troubleshooting

#### Connection Refused Error
-   **Is qBittorrent running?** The application must be active for the script to connect.
-   **Is the Web UI enabled?** Double-check the settings in qBittorrent.
-   **Is the port correct?** Verify the port number matches the one in the Web UI settings.
-   **Firewall blockage:** Ensure your firewall is not blocking the connection to the specified port.

#### Login Failed
-   **Check credentials:** Carefully re-enter your username and password.
-   **Authentication enabled:** Make sure authentication is required in the Web UI settings.
-   **IP Banned:** qBittorrent may ban an IP after too many failed login attempts. Check the settings in **Tools → Options → Web UI → "Ban client after consecutive failed authentication attempts"**.

#### Permission Denied
-   **Read Access:** The script needs read permissions for your download directory to scan for files.
-   **Write/Delete Access:** To delete files, the script needs write permissions.
-   **Run with elevated privileges:** If necessary, run the script with `sudo` (`sudo python3 qbittorrent-orphan-cleaner.py`), but be extremely cautious, especially when deleting files.

---

## ⚠️ Safety Notes

-   **Review Before Deletion:** The script will **always** show you a count and total size of files it intends to delete before proceeding.
-   **Explicit Confirmation:** You must type `DELETE` in all caps to confirm the file deletion process. This is a deliberate safety measure to prevent accidental data loss.
-   **Pre-deletion Report:** A detailed report (`orphaned_files.txt`) is saved to your home directory **before** any deletion occurs. You can review this file to see exactly what will be removed.
-   **Backup First:** It is always a good practice to back up any critical data in your download directory before running a cleaning script.

## Contributing

Contributions are welcome! Feel free to open an issue to report bugs or suggest improvements, or submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
