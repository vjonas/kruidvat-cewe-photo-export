#!/usr/bin/env python3
"""
Web interface for CEWE Photo Book Fetcher
Provides a web UI to run the shell scripts and CEWE URL fetcher
"""

import os
import subprocess
import threading
import time
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from flask_socketio import SocketIO, emit
import logging
from datetime import datetime
import sys

# Add current directory to path so we can import our scripts
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try to import our CEWE fetcher
try:
    from cewe_fetcher import CEWEPhotoBookFetcher
    CEWE_FETCHER_AVAILABLE = True
except ImportError:
    CEWE_FETCHER_AVAILABLE = False
    print("⚠️ CEWE fetcher not available. Install required dependencies.")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
socketio = SocketIO(app, cors_allowed_origins="*")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScriptRunner:
    def __init__(self):
        self.running_processes = {}
        self.process_outputs = {}
        self.running_fetchers = {}  # For CEWE fetcher instances
    
    def run_script(self, script_name, script_path, options=None):
        """Run a script and stream its output"""
        if script_name in self.running_processes:
            return False, "Script is already running"
        
        try:
            # Prepare command
            cmd = ['/bin/bash', script_path]
            if options:
                cmd.extend(options)
            
            # Start process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                cwd=os.getcwd()
            )
            
            self.running_processes[script_name] = process
            self.process_outputs[script_name] = []
            
            # Start output streaming thread
            threading.Thread(
                target=self._stream_output,
                args=(script_name, process),
                daemon=True
            ).start()
            
            return True, "Script started successfully"
            
        except Exception as e:
            logger.error(f"Error running script {script_name}: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def run_cewe_fetcher(self, script_name, photobook_url, start_page=1, end_page=None, width=1080):
        """Run CEWE fetcher directly"""
        if not CEWE_FETCHER_AVAILABLE:
            return False, "CEWE fetcher not available. Install required dependencies."
            
        if script_name in self.running_fetchers:
            return False, "CEWE fetcher is already running"
        
        try:
            # Create fetcher instance
            fetcher = CEWEPhotoBookFetcher(
                photobook_url=photobook_url,
                start_page=start_page,
                end_page=end_page,
                target_width=width
            )
            
            self.running_fetchers[script_name] = fetcher
            self.process_outputs[script_name] = []
            
            # Start fetcher thread
            threading.Thread(
                target=self._run_cewe_fetcher_thread,
                args=(script_name, fetcher),
                daemon=True
            ).start()
            
            return True, "CEWE fetcher started successfully"
            
        except Exception as e:
            logger.error(f"Error running CEWE fetcher {script_name}: {str(e)}")
            return False, f"Error: {str(e)}"
    
    def _run_cewe_fetcher_thread(self, script_name, fetcher):
        """Run CEWE fetcher in a separate thread"""
        try:
            # Redirect stdout to capture prints
            import io
            import contextlib
            
            output_buffer = io.StringIO()
            
            def emit_output(message):
                self.process_outputs[script_name].append(message)
                socketio.emit('script_output', {
                    'script': script_name,
                    'output': message,
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
            
            # Override print function temporarily
            original_print = print
            def custom_print(*args, **kwargs):
                message = ' '.join(str(arg) for arg in args)
                emit_output(message)
                original_print(*args, **kwargs)
            
            # Replace print globally for the fetcher
            import builtins
            builtins.print = custom_print
            
            try:
                # Run the fetcher
                success = fetcher.run()
                
                if success:
                    emit_output("🎉 CEWE photo book fetched successfully!")
                    socketio.emit('script_finished', {
                        'script': script_name,
                        'return_code': 0,
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    })
                else:
                    emit_output("❌ CEWE photo book fetch failed!")
                    socketio.emit('script_finished', {
                        'script': script_name,
                        'return_code': 1,
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    })
                    
            finally:
                # Restore original print
                builtins.print = original_print
                
        except Exception as e:
            logger.error(f"Error in CEWE fetcher thread {script_name}: {str(e)}")
            socketio.emit('script_error', {
                'script': script_name,
                'error': str(e),
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
        finally:
            # Clean up
            if script_name in self.running_fetchers:
                del self.running_fetchers[script_name]
    
    def _stream_output(self, script_name, process):
        """Stream process output via websocket"""
        try:
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    line = output.strip()
                    self.process_outputs[script_name].append(line)
                    socketio.emit('script_output', {
                        'script': script_name,
                        'output': line,
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    })
            
            # Process finished
            return_code = process.poll()
            socketio.emit('script_finished', {
                'script': script_name,
                'return_code': return_code,
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
            
        except Exception as e:
            logger.error(f"Error streaming output for {script_name}: {str(e)}")
            socketio.emit('script_error', {
                'script': script_name,
                'error': str(e),
                'timestamp': datetime.now().strftime('%H:%M:%S')
            })
        finally:
            # Clean up
            if script_name in self.running_processes:
                del self.running_processes[script_name]
    
    def stop_script(self, script_name):
        """Stop a running script or fetcher"""
        # Try to stop regular script first
        if script_name in self.running_processes:
            try:
                self.running_processes[script_name].terminate()
                del self.running_processes[script_name]
                return True, "Script stopped"
            except Exception as e:
                return False, f"Error stopping script: {str(e)}"
        
        # Try to stop CEWE fetcher
        if script_name in self.running_fetchers:
            try:
                # There's no clean way to stop the fetcher mid-execution
                # But we can remove it from tracking
                del self.running_fetchers[script_name]
                return True, "CEWE fetcher stopped"
            except Exception as e:
                return False, f"Error stopping CEWE fetcher: {str(e)}"
        
        return False, "Script not running"
    
    def is_running(self, script_name):
        """Check if a script or fetcher is running"""
        return script_name in self.running_processes or script_name in self.running_fetchers
    
    def get_output(self, script_name):
        """Get accumulated output for a script"""
        return self.process_outputs.get(script_name, [])

# Global script runner instance
script_runner = ScriptRunner()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html', cewe_available=CEWE_FETCHER_AVAILABLE)

@app.route('/run_script', methods=['POST'])
def run_script():
    """Run a script"""
    data = request.json
    script_name = data.get('script')
    options = data.get('options', [])
    
    if script_name == 'photobook':
        success, message = script_runner.run_script('photobook', './run_web.sh', options)
    elif script_name == 'spreads':
        success, message = script_runner.run_script('spreads', './run_spreads.sh', options)
    else:
        return jsonify({'success': False, 'message': 'Unknown script'})
    
    return jsonify({'success': success, 'message': message})

@app.route('/run_cewe_fetcher', methods=['POST'])
def run_cewe_fetcher():
    """Run CEWE photo book fetcher with URL"""
    data = request.json
    
    photobook_url = data.get('url', '').strip()
    start_page = int(data.get('start_page', 1))
    end_page = data.get('end_page')
    if end_page:
        end_page = int(end_page)
    width = int(data.get('width', 1080))
    
    if not photobook_url:
        return jsonify({'success': False, 'message': 'Photo book URL is required'})
    
    if not photobook_url.startswith('http'):
        return jsonify({'success': False, 'message': 'Invalid URL format'})
    
    success, message = script_runner.run_cewe_fetcher(
        'cewe_fetcher', 
        photobook_url, 
        start_page, 
        end_page, 
        width
    )
    
    return jsonify({'success': success, 'message': message})

@app.route('/stop_script', methods=['POST'])
def stop_script():
    """Stop a running script"""
    data = request.json
    script_name = data.get('script')
    
    success, message = script_runner.stop_script(script_name)
    return jsonify({'success': success, 'message': message})

@app.route('/script_status/<script_name>')
def script_status(script_name):
    """Get script status"""
    return jsonify({
        'running': script_runner.is_running(script_name),
        'output': script_runner.get_output(script_name)
    })

@app.route('/download/<filename>')
def download_file(filename):
    """Download generated files"""
    output_dir = os.path.join(os.getcwd(), 'output')
    file_path = os.path.join(output_dir, filename)
    
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404

@app.route('/list_files')
def list_files():
    """List available files for download"""
    output_dir = os.path.join(os.getcwd(), 'output')
    files = []
    
    if os.path.exists(output_dir):
        for file in os.listdir(output_dir):
            if file.endswith('.pdf'):
                file_path = os.path.join(output_dir, file)
                file_size = os.path.getsize(file_path)
                file_time = os.path.getmtime(file_path)
                files.append({
                    'name': file,
                    'size': file_size,
                    'modified': datetime.fromtimestamp(file_time).strftime('%Y-%m-%d %H:%M:%S')
                })
    
    return jsonify({'files': files})

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('connected', {'message': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

if __name__ == '__main__':
    # Make sure output directory exists
    os.makedirs('output', exist_ok=True)
    
    # Start the web server
    print("🚀 Starting Enhanced CEWE Photo Book Fetcher Web Interface...")
    print("📱 Access the web interface at: http://localhost:4200")
    print("🔧 Make sure to run this in the same directory as your scripts")
    
    if CEWE_FETCHER_AVAILABLE:
        print("✅ CEWE URL fetcher available")
    else:
        print("⚠️ CEWE URL fetcher not available - install dependencies")
    
    socketio.run(app, host='0.0.0.0', port=4200, debug=False)