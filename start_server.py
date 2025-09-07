#!/usr/bin/env python3
"""
Script to start the e-commerce backend server
"""

import subprocess
import sys
import os
import time

def kill_port_process(port):
    """Kill any process using the specified port"""
    try:
        # Find process using the port
        result = subprocess.run(
            f'netstat -ano | findstr :{port}',
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        print(f"Killing process {pid} using port {port}")
                        subprocess.run(f'taskkill /F /PID {pid}', shell=True)
                        time.sleep(1)
    except Exception as e:
        print(f"Error killing process on port {port}: {e}")

def start_server():
    """Start the FastAPI server"""
    print("Starting E-commerce API server...")
    
    # Kill any existing process on port 8001
    kill_port_process(8001)
    
    # Start the server
    try:
        os.chdir('backend')
        subprocess.run([sys.executable, '-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8001', '--reload'])
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")

if __name__ == "__main__":
    start_server()