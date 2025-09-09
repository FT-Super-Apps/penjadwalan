#!/usr/bin/env python3
"""
Enhanced University Scheduling System - Web Interface Launcher
Production-ready launcher with proper configuration
"""

import os
import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app import app

def setup_production_config():
    """Setup production configuration"""
    app.config.update({
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'your-super-secret-production-key-change-this'),
        'DEBUG': False,
        'TESTING': False,
        'MAX_CONTENT_LENGTH': 32 * 1024 * 1024,  # 32MB for production
        'UPLOAD_FOLDER': os.environ.get('UPLOAD_FOLDER', 'uploads'),
        'DATABASE_URL': os.environ.get('DATABASE_URL', 'sqlite:///scheduling.db'),
    })

def setup_development_config():
    """Setup development configuration"""
    app.config.update({
        'SECRET_KEY': 'dev-secret-key-not-for-production',
        'DEBUG': True,
        'TESTING': False,
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB for development
        'UPLOAD_FOLDER': 'uploads',
    })

def main():
    """Main application launcher"""
    parser = argparse.ArgumentParser(description='Enhanced University Scheduling System')
    parser.add_argument('--mode', choices=['dev', 'prod'], default='dev',
                      help='Run mode: dev or prod (default: dev)')
    parser.add_argument('--host', default='127.0.0.1',
                      help='Host to bind to (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=5000,
                      help='Port to bind to (default: 5000)')
    parser.add_argument('--workers', type=int, default=4,
                      help='Number of worker processes for production (default: 4)')
    
    args = parser.parse_args()
    
    # Ensure upload directory exists
    upload_dir = 'uploads'
    os.makedirs(upload_dir, exist_ok=True)
    
    print("🎓 Enhanced University Scheduling System")
    print("=" * 50)
    
    if args.mode == 'prod':
        print("🚀 Starting in PRODUCTION mode")
        setup_production_config()
        
        try:
            import gunicorn.app.wsgiapp as wsgi
            sys.argv = [
                'gunicorn',
                '--bind', f'{args.host}:{args.port}',
                '--workers', str(args.workers),
                '--worker-class', 'gevent',
                '--worker-connections', '1000',
                '--max-requests', '1000',
                '--max-requests-jitter', '100',
                '--timeout', '300',
                '--keep-alive', '5',
                '--access-logfile', '-',
                '--error-logfile', '-',
                '--log-level', 'info',
                'app:app'
            ]
            wsgi.run()
        except ImportError:
            print("❌ Gunicorn not installed. Install with: pip install gunicorn gevent")
            print("🔄 Falling back to Flask dev server (not recommended for production)")
            app.run(host=args.host, port=args.port, threaded=True)
    
    else:
        print("🛠️  Starting in DEVELOPMENT mode")
        setup_development_config()
        
        print(f"🌐 Server running at: http://{args.host}:{args.port}")
        print(f"📁 Upload folder: {app.config['UPLOAD_FOLDER']}")
        print(f"📊 Max file size: {app.config['MAX_CONTENT_LENGTH'] / (1024*1024):.0f}MB")
        print(f"🔧 Debug mode: {app.config['DEBUG']}")
        print("=" * 50)
        print("\n💡 Tips:")
        print("  - Upload CSV or Excel files with your course data")
        print("  - Configure algorithm parameters for better results")
        print("  - Use export functions to save your optimized schedule")
        print("  - Press Ctrl+C to stop the server")
        print()
        
        try:
            app.run(
                host=args.host,
                port=args.port,
                debug=True,
                threaded=True,
                use_reloader=True
            )
        except KeyboardInterrupt:
            print("\n👋 Server stopped by user")
        except Exception as e:
            print(f"❌ Server error: {e}")
            sys.exit(1)

if __name__ == '__main__':
    main()