import sys
import os
import re
import json
import subprocess
import shutil
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QComboBox, QProgressBar, QTextEdit, QMessageBox,
                             QFileDialog, QScrollArea, QFrame, QGridLayout)

import yt_dlp
import urllib.request
import glob

class DownloadThread(QThread):
    progress_signal = pyqtSignal(int, int, int, str)  # current, total, percentage, playlist_name
    log_signal = pyqtSignal(str, str)  # message, playlist_name
    finished_signal = pyqtSignal(bool, str, str)  # success, message, playlist_name
    playlist_start_signal = pyqtSignal(str, int)  # playlist_name, total_videos

    def __init__(self, playlist_urls, format_choice, output_path):
        super().__init__()
        self.playlist_urls = playlist_urls
        self.format_choice = format_choice
        self.output_path = output_path
        self.is_running = True
        self.ffmpeg_path = self.find_ffmpeg()

    def find_ffmpeg(self):
        """Find FFmpeg executable path"""
        # Check if ffmpeg is in PATH
        ffmpeg_path = shutil.which('ffmpeg')
        if ffmpeg_path:
            return ffmpeg_path
            
        # Check common installation paths for winget installation
        possible_paths = [
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'WinGet', 'Packages', 'Gyan.FFmpeg.Essentials_*', 'bin', 'ffmpeg.exe'),
            os.path.join(os.environ.get('PROGRAMFILES', ''), 'ffmpeg', 'bin', 'ffmpeg.exe'),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'ffmpeg', 'bin', 'ffmpeg.exe'),
            'C:\\ffmpeg\\bin\\ffmpeg.exe',
            os.path.expanduser('~\\ffmpeg\\bin\\ffmpeg.exe'),
        ]
        
        # Expand wildcards and check each path
        for path_pattern in possible_paths:
            expanded_paths = glob.glob(path_pattern)
            for path in expanded_paths:
                if os.path.exists(path):
                    return path
                    
        return None

    def check_ffmpeg(self):
        """Check if FFmpeg is available"""
        if self.ffmpeg_path and os.path.exists(self.ffmpeg_path):
            try:
                result = subprocess.run([self.ffmpeg_path, '-version'], 
                                      capture_output=True, text=True, timeout=10)
                return result.returncode == 0
            except:
                return False
        return False

    def get_playlist_info(self, playlist_url):
        """Get playlist information using yt-dlp"""
        try:
            ydl_opts = {
                'quiet': True,
                'extract_flat': True,
                'force_json': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(playlist_url, download=False)
                return info
        except Exception as e:
            self.log_signal.emit(f"Error getting playlist info: {str(e)}", self.get_playlist_name(playlist_url))
            return None

    def get_playlist_name(self, playlist_url):
        """Extract playlist name from URL or use a default name"""
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(playlist_url, download=False)
                return info.get('title', f"Playlist_{hash(playlist_url)}")
        except:
            return f"Playlist_{hash(playlist_url)}"

    def download_video(self, video_url, index, total, playlist_name):
        """Download individual video using yt-dlp"""
        try:
            # Set options based on format choice
            if self.format_choice == "mp3":
                # Check if FFmpeg is available for MP3 conversion
                if not self.check_ffmpeg():
                    self.log_signal.emit("FFmpeg not found. Downloading as best audio format...", playlist_name)
                    # Fallback: download as best audio without conversion
                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'outtmpl': os.path.join(self.output_path, playlist_name, '%(title)s.%(ext)s'),
                        'quiet': True,
                        'no_warnings': True,
                    }
                else:
                    # Use FFmpeg for MP3 conversion with explicit path
                    ydl_opts = {
                        'format': 'bestaudio/best',
                        'outtmpl': os.path.join(self.output_path, playlist_name, '%(title)s.%(ext)s'),
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
                        'ffmpeg_location': os.path.dirname(self.ffmpeg_path),
                        'quiet': True,
                        'no_warnings': True,
                    }
            else:  # mp4
                ydl_opts = {
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'outtmpl': os.path.join(self.output_path, playlist_name, '%(title)s.%(ext)s'),
                    'merge_output_format': 'mp4',
                    'quiet': True,
                    'no_warnings': True,
                }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                self.log_signal.emit(f"✓ Downloaded: {info.get('title', 'Unknown')}", playlist_name)
                return True
                
        except Exception as e:
            error_msg = str(e)
            # Clean up error message by removing ANSI color codes
            clean_error = re.sub(r'\x1b\[[0-9;]*m', '', error_msg)
            self.log_signal.emit(f"✗ Error downloading video: {clean_error}", playlist_name)
            return False

    def run(self):
        try:
            # Check for FFmpeg if MP3 is selected
            if self.format_choice == "mp3":
                if self.check_ffmpeg():
                    self.log_signal.emit(f"✅ Using FFmpeg at: {self.ffmpeg_path}", "System")
                else:
                    self.log_signal.emit("⚠️ FFmpeg not found. Audio files will be downloaded in original format.", "System")
                    self.log_signal.emit("You can convert them to MP3 later using other tools.", "System")
            
            # Create main output directory if it doesn't exist
            if not os.path.exists(self.output_path):
                os.makedirs(self.output_path)

            total_successful = 0
            total_videos_all = 0
            
            for playlist_url in self.playlist_urls:
                if not self.is_running:
                    break
                    
                playlist_name = self.get_playlist_name(playlist_url)
                
                # Create playlist-specific directory
                playlist_output_path = os.path.join(self.output_path, playlist_name)
                if not os.path.exists(playlist_output_path):
                    os.makedirs(playlist_output_path)

                # Get playlist information
                self.log_signal.emit("Getting playlist information...", playlist_name)
                playlist_info = self.get_playlist_info(playlist_url)
                
                if not playlist_info or 'entries' not in playlist_info:
                    self.log_signal.emit("Could not retrieve playlist information.", playlist_name)
                    continue
                
                # Extract video URLs
                video_urls = []
                for entry in playlist_info['entries']:
                    if entry and 'url' in entry:
                        video_urls.append(entry['url'])
                
                total_videos = len(video_urls)
                if total_videos == 0:
                    self.log_signal.emit("No videos found in the playlist.", playlist_name)
                    continue
                    
                total_videos_all += total_videos
                self.playlist_start_signal.emit(playlist_name, total_videos)
                self.log_signal.emit(f"Found {total_videos} videos in the playlist", playlist_name)
                
                successful_downloads = 0
                
                for index, video_url in enumerate(video_urls, 1):
                    if not self.is_running:
                        break
                    
                    # Update progress
                    progress = int((index) / total_videos * 100)
                    self.progress_signal.emit(index, total_videos, progress, playlist_name)
                    
                    # Download the video
                    if self.download_video(video_url, index, total_videos, playlist_name):
                        successful_downloads += 1
                
                total_successful += successful_downloads
                self.log_signal.emit(f"Playlist completed: {successful_downloads}/{total_videos} videos downloaded", playlist_name)
            
            if self.is_running:
                message = f"All downloads completed! {total_successful}/{total_videos_all} videos downloaded successfully across {len(self.playlist_urls)} playlists."
                self.finished_signal.emit(True, message, "System")
            else:
                self.finished_signal.emit(False, "Download cancelled by user.", "System")
            
        except Exception as e:
            self.finished_signal.emit(False, f"Error: {str(e)}", "System")
    
    def stop(self):
        self.is_running = False

class FFmpegChecker(QThread):
    finished_signal = pyqtSignal(bool, str)
    
    def run(self):
        """Check if FFmpeg is available"""
        try:
            # Check if ffmpeg is in PATH
            ffmpeg_path = shutil.which('ffmpeg')
            if ffmpeg_path:
                self.finished_signal.emit(True, ffmpeg_path)
                return
                
            # Check common installation paths
            possible_paths = [
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'WinGet', 'Packages', 'Gyan.FFmpeg.Essentials_*', 'bin', 'ffmpeg.exe'),
                os.path.join(os.environ.get('PROGRAMFILES', ''), 'ffmpeg', 'bin', 'ffmpeg.exe'),
                os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'ffmpeg', 'bin', 'ffmpeg.exe'),
                'C:\\ffmpeg\\bin\\ffmpeg.exe',
                os.path.expanduser('~\\ffmpeg\\bin\\ffmpeg.exe'),
            ]
            
            # Expand wildcards and check each path
            for path_pattern in possible_paths:
                expanded_paths = glob.glob(path_pattern)
                for path in expanded_paths:
                    if os.path.exists(path):
                        self.finished_signal.emit(True, path)
                        return
            
            self.finished_signal.emit(False, "")
            
        except Exception as e:
            self.finished_signal.emit(False, str(e))

class YouTubeDownloaderApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.download_thread = None
        self.ffmpeg_checker = None
        self.playlist_progress_bars = {}  # Store progress bars for each playlist
        self.playlist_labels = {}  # Store labels for each playlist

    def initUI(self):
        self.setWindowTitle('YouTube Multi-Playlist Downloader')
        self.setGeometry(100, 100, 800, 700)
        
        # Central widget with scroll area
        central_widget = QWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(central_widget)
        self.setCentralWidget(scroll_area)
        
        # Layouts
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Title
        title_label = QLabel('YouTube Multi-Playlist Downloader')
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px; padding: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # FFmpeg status
        self.ffmpeg_status = QLabel('Checking FFmpeg...')
        self.ffmpeg_status.setStyleSheet("color: orange; font-weight: bold;")
        self.ffmpeg_status.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.ffmpeg_status)
        
        # Playlist URLs section
        urls_frame = QFrame()
        urls_frame.setFrameStyle(QFrame.Box)
        urls_layout = QVBoxLayout(urls_frame)
        
        urls_label = QLabel('Playlist URLs (one per line):')
        urls_label.setStyleSheet("font-weight: bold;")
        urls_layout.addWidget(urls_label)
        
        self.urls_input = QTextEdit()
        self.urls_input.setPlaceholderText('https://www.youtube.com/playlist?list=...\nhttps://www.youtube.com/playlist?list=...\nhttps://www.youtube.com/playlist?list=...')
        self.urls_input.setMaximumHeight(100)
        urls_layout.addWidget(self.urls_input)
        
        main_layout.addWidget(urls_frame)
        
        # Format selection and output path
        options_layout = QHBoxLayout()
        
        # Format selection
        format_layout = QVBoxLayout()
        format_label = QLabel('Format:')
        format_label.setStyleSheet("font-weight: bold;")
        self.format_combo = QComboBox()
        self.format_combo.addItems(['mp4', 'mp3'])
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo)
        options_layout.addLayout(format_layout)
        
        # Output path
        path_layout = QVBoxLayout()
        path_label = QLabel('Output Folder:')
        path_label.setStyleSheet("font-weight: bold;")
        path_input_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setText(os.path.expanduser('~/Downloads/YouTube_Playlists'))
        browse_btn = QPushButton('Browse')
        browse_btn.clicked.connect(self.browse_folder)
        path_input_layout.addWidget(self.path_input)
        path_input_layout.addWidget(browse_btn)
        path_layout.addWidget(path_label)
        path_layout.addLayout(path_input_layout)
        options_layout.addLayout(path_layout)
        
        main_layout.addLayout(options_layout)
        
        # Progress section
        progress_frame = QFrame()
        progress_frame.setFrameStyle(QFrame.Box)
        progress_layout = QVBoxLayout(progress_frame)
        
        progress_title = QLabel('Download Progress')
        progress_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        progress_title.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(progress_title)
        
        # Container for individual playlist progress
        self.progress_container = QWidget()
        self.progress_container_layout = QVBoxLayout(self.progress_container)
        progress_layout.addWidget(self.progress_container)
        
        main_layout.addWidget(progress_frame)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.download_btn = QPushButton('Download All Playlists')
        self.download_btn.clicked.connect(self.start_download)
        self.download_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 8px; }")
        
        self.cancel_btn = QPushButton('Cancel All')
        self.cancel_btn.clicked.connect(self.cancel_download)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-weight: bold; padding: 8px; }")
        
        button_layout.addWidget(self.download_btn)
        button_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(button_layout)
        
        # Log area
        log_label = QLabel('Download Log:')
        log_label.setStyleSheet("font-weight: bold;")
        main_layout.addWidget(log_label)
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        main_layout.addWidget(self.log_area)
        
        # Check FFmpeg status
        QTimer.singleShot(0, self.check_ffmpeg_status)

    def add_playlist_progress(self, playlist_name, total_videos):
        """Add progress bar for a new playlist"""
        # Remove existing progress if it exists
        if playlist_name in self.playlist_progress_bars:
            old_progress = self.playlist_progress_bars[playlist_name]
            old_label = self.playlist_labels[playlist_name]
            self.progress_container_layout.removeWidget(old_progress)
            self.progress_container_layout.removeWidget(old_label)
            old_progress.deleteLater()
            old_label.deleteLater()
        
        # Create new progress elements
        playlist_label = QLabel(f"{playlist_name}: 0/{total_videos} videos")
        playlist_label.setStyleSheet("font-weight: bold; margin-top: 5px;")
        
        progress_bar = QProgressBar()
        progress_bar.setValue(0)
        progress_bar.setFormat(f"{playlist_name} - %p%")
        
        # Store references
        self.playlist_labels[playlist_name] = playlist_label
        self.playlist_progress_bars[playlist_name] = progress_bar
        
        # Add to layout
        self.progress_container_layout.addWidget(playlist_label)
        self.progress_container_layout.addWidget(progress_bar)

    def check_ffmpeg_status(self):
        """Check if FFmpeg is available and update status"""
        self.ffmpeg_checker = FFmpegChecker()
        self.ffmpeg_checker.finished_signal.connect(self.update_ffmpeg_status)
        self.ffmpeg_checker.start()
        
    def update_ffmpeg_status(self, status, path):
        if status:
            self.ffmpeg_status.setText(f'FFmpeg: ✅ Installed at {path}')
            self.ffmpeg_status.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.ffmpeg_status.setText('FFmpeg: ❌ Not found (MP3 conversion will not work)')
            self.ffmpeg_status.setStyleSheet("color: red; font-weight: bold;")

        if self.ffmpeg_checker and self.ffmpeg_checker.isRunning():
            self.ffmpeg_checker.wait()
        self.ffmpeg_checker = None

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select Output Folder')
        if folder:
            self.path_input.setText(folder)
    
    def start_download(self):
        urls_text = self.urls_input.toPlainText().strip()
        if not urls_text:
            QMessageBox.warning(self, 'Input Error', 'Please enter at least one YouTube playlist URL')
            return
        
        # Parse URLs (split by newlines and filter empty lines)
        playlist_urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
        
        # Validate URLs
        valid_urls = []
        for url in playlist_urls:
            if 'playlist?list=' in url or 'list=' in url:
                valid_urls.append(url)
            else:
                self.log_area.append(f"❌ Invalid playlist URL: {url}")
        
        if not valid_urls:
            QMessageBox.warning(self, 'Input Error', 'Please enter valid YouTube playlist URLs')
            return
        
        output_path = self.path_input.text().strip()
        if not output_path:
            QMessageBox.warning(self, 'Input Error', 'Please select an output folder')
            return
        
        format_choice = self.format_combo.currentText()
        
        # Warn about FFmpeg if MP3 is selected
        if format_choice == "mp3":
            reply = QMessageBox.question(self, 'FFmpeg Check', 
                                       'MP3 conversion requires FFmpeg.\n\n'
                                       'Do you want to continue?',
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.No:
                return
        
        # Disable UI elements during download
        self.download_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.urls_input.setEnabled(False)
        self.format_combo.setEnabled(False)
        self.path_input.setEnabled(False)
        
        # Clear previous log and progress
        self.log_area.clear()
        self.playlist_progress_bars.clear()
        self.playlist_labels.clear()
        
        # Clear progress container
        for i in reversed(range(self.progress_container_layout.count())): 
            self.progress_container_layout.itemAt(i).widget().setParent(None)
        
        self.log_area.append("🚀 Starting download of multiple playlists...")
        
        # Start download thread
        self.download_thread = DownloadThread(valid_urls, format_choice, output_path)
        self.download_thread.progress_signal.connect(self.update_progress)
        self.download_thread.log_signal.connect(self.update_log)
        self.download_thread.finished_signal.connect(self.download_finished)
        self.download_thread.playlist_start_signal.connect(self.add_playlist_progress)
        self.download_thread.start()
    
    def cancel_download(self):
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.stop()
            self.download_thread.wait()
            self.log_area.append("⏹️ Download cancelled by user")
            self.reset_ui()
    
    def update_progress(self, current, total, percentage, playlist_name):
        """Update progress for a specific playlist"""
        if playlist_name in self.playlist_progress_bars:
            self.playlist_progress_bars[playlist_name].setValue(percentage)
        if playlist_name in self.playlist_labels:
            self.playlist_labels[playlist_name].setText(f"{playlist_name}: {current}/{total} videos")
    
    def update_log(self, message, playlist_name):
        """Add log message with playlist context"""
        if playlist_name != "System":
            formatted_message = f"[{playlist_name}] {message}"
        else:
            formatted_message = message
        
        self.log_area.append(formatted_message)
        # Auto-scroll to bottom
        self.log_area.verticalScrollBar().setValue(
            self.log_area.verticalScrollBar().maximum()
        )
    
    def download_finished(self, success, message, playlist_name):
        if success:
            self.log_area.append(f"✅ {message}")
            QMessageBox.information(self, 'Success', message)
        else:
            self.log_area.append(f"❌ {message}")
            QMessageBox.warning(self, 'Download Status', message)
        
        self.reset_ui()
    
    def reset_ui(self):
        self.download_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.urls_input.setEnabled(True)
        self.format_combo.setEnabled(True)
        self.path_input.setEnabled(True)
    
    def closeEvent(self, event):
        if self.download_thread and self.download_thread.isRunning():
            reply = QMessageBox.question(
                self, 'Download in Progress',
                'A download is in progress. Are you sure you want to quit?',
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.download_thread.stop()
                self.download_thread.wait()
            else:
                event.ignore()
                return

        if self.ffmpeg_checker and self.ffmpeg_checker.isRunning():
            self.ffmpeg_checker.wait()

        event.accept()

def main():
    app = QApplication(sys.argv)
    window = YouTubeDownloaderApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()