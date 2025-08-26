# YouTube Multi-Playlist Downloader

A powerful PyQt5-based desktop application for downloading multiple YouTube playlists simultaneously with individual progress tracking for each playlist.

![YouTube Downloader](https://img.shields.io/badge/YouTube-Downloader-red?style=for-the-badge&logo=youtube)
![Python](https://img.shields.io/badge/Python-3.7%2B-blue?style=for-the-badge&logo=python)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-green?style=for-the-badge&logo=qt)

## ✨ Features

- **📥 Multiple Playlist Support** - Download multiple YouTube playlists simultaneously
- **🎵 Format Options** - Choose between MP4 (video) or MP3 (audio) format
- **📊 Individual Progress Tracking** - Separate progress bars for each playlist
- **🔍 Smart FFmpeg Detection** - Automatic detection of FFmpeg installation
- **🎯 User-Friendly GUI** - Clean and intuitive PyQt5 interface
- **⏯️ Download Control** - Cancel downloads at any time
- **📝 Comprehensive Logging** - Detailed download logs with timestamps
- **🖥️ Cross-Platform** - Works on Windows, Linux, and macOS

## 📦 Installation

### Prerequisites

- Python 3.7 or higher
- FFmpeg (required for MP3 conversion, optional for MP4)

### Method 1: Using pip

1. **Clone the repository**:
   ```bash
   git clone https://github.com/elachraf48/youtube-multi-playlist-downloader.git
   cd youtube-multi-playlist-downloader
Install dependencies:

pip install -r requirements.txt
Method 2: Direct download
Download the youtube_downloader.py file

Install required packages:

pip install PyQt5 yt-dlp pyyaml
FFmpeg Installation
Windows:

winget install Gyan.FFmpeg.Essentials
Linux (Ubuntu/Debian):


sudo apt update
sudo apt install ffmpeg
macOS:


brew install ffmpeg
🚀 Usage
Launch the application:


python youtube_downloader.py
Interface Overview:

Playlist URLs: Enter one YouTube playlist URL per line

Format Selection: Choose MP4 (video) or MP3 (audio)

Output Folder: Select where to save downloaded files

Progress Section: Individual progress bars for each playlist

Log Area: Real-time download status and messages

Download Process:

Enter playlist URLs in the text area

Select your preferred format (MP4/MP3)

Choose output directory

Click "Download All Playlists"

Monitor progress in real-time

🔗 How to Get YouTube Playlist URLs
Navigate to the YouTube playlist in your web browser

Copy the URL from the address bar

The URL should contain list= parameter:


https://www.youtube.com/playlist?list=PLxxxxxxxxxxxxxxxxxxxx
🛠️ Technical Details
Dependencies
PyQt5: GUI framework

yt-dlp: YouTube video downloading backend

PyYAML: Configuration file handling

Project Structure
youtube-multi-playlist-downloader/
│
├── youtube_downloader.py    # Main application file
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── .gitignore             # Git ignore rules
⚙️ Configuration
The application automatically:

Detects FFmpeg installation locations

Creates organized folder structure for downloads

Handles network interruptions gracefully

Preserves download progress across sessions

🐛 Troubleshooting
Common Issues
"FFmpeg not found" error:

Install FFmpeg using the instructions above

Or use MP4 format instead of MP3

Download failures:

Check internet connection

Verify playlist URLs are correct and accessible

Ensure playlists are not private or age-restricted

Permission errors:

Run as administrator (Windows)

Choose a different output directory with write permissions

Application crashes:

Ensure all dependencies are installed:

pip install -r requirements.txt
Debug Mode
For detailed error information, run with debug output:

python youtube_downloader.py --debug
📋 Requirements
Python 3.7+

100MB+ free disk space

Internet connection

FFmpeg (for MP3 conversion)

🤝 Contributing
Contributions are welcome! Here's how you can help:

Fork the repository

Create a feature branch: git checkout -b feature/amazing-feature

Commit your changes: git commit -m 'Add amazing feature'

Push to the branch: git push origin feature/amazing-feature

Open a Pull Request

Development Setup
# Clone the repository
git clone https://github.com/your-username/youtube-multi-playlist-downloader.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
📜 License
This project is for educational and personal use only. Users are responsible for complying with:

YouTube's Terms of Service

Copyright laws in their country

Fair use regulations

⚠️ Disclaimer
This software is provided "as is" without any warranties. The developers are not responsible for:

How users employ this tool

Any copyright infringements that may occur

Damage to computer systems or data loss

Legal consequences of downloading content

Use this application responsibly and only download content you have rights to access.

📞 Support
If you encounter issues:

Check the troubleshooting section above

Search existing GitHub issues

Create a new issue with:

Error messages

Steps to reproduce

System information

🎉 Acknowledgments
yt-dlp for the YouTube downloading backend

FFmpeg for audio/video processing

PyQt5 for the GUI framework

⭐ If you find this project useful, please give it a star on GitHub!



This README.md file includes:

1. **Eye-catching badges** for better visual appeal
2. **Comprehensive feature list** with emojis
3. **Detailed installation instructions** for all platforms
4. **Step-by-step usage guide**
5. **Troubleshooting section** for common issues
6. **Technical details** about dependencies and structure
7. **Contribution guidelines**
8. **Legal disclaimer** and license information
9. **Support information**
10. **Acknowledgments**

The file is well-organized with clear sections and uses GitHub-flavored markdown for better readability. You can copy this directly into your repository!
