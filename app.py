from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import yt_dlp
import os

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'jar_yt_secure_key'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/get-info', methods=['POST'])
def get_video_info():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        # --- NEW SETTINGS TO BYPASS BOT CHECK ---
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best',
            'nocheckcertificate': True,
            # YouTube ko lagega ye request Android phone se aa rahi hai
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'ios'],
                }
            },
            # Fake User Agent
            'user_agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            video_data = {
                'title': info.get('title', 'Unknown Title'),
                'thumbnail': info.get('thumbnail'),
                'duration': info.get('duration_string'),
                'views': info.get('view_count'),
                'formats': []
            }

            for f in info['formats']:
                if f.get('ext') == 'mp4' and f.get('acodec') != 'none' and f.get('vcodec') != 'none':
                    filesize = f.get('filesize', 0) or 0
                    filesize_mb = round(filesize / (1024 * 1024), 1) if filesize else "N/A"
                    
                    video_data['formats'].append({
                        'quality': f.get('format_note', 'HD'),
                        'resolution': f.get('resolution'),
                        'size': f"{filesize_mb} MB",
                        'url': f.get('url'),
                        'type': 'video'
                    })

            # Audio Only
            audio_url = next((f['url'] for f in info['formats'] if f.get('acodec') != 'none' and f.get('vcodec') == 'none'), '#')
            video_data['formats'].append({
                'quality': 'Audio (MP3)',
                'resolution': 'Audio Only',
                'size': 'N/A',
                'url': audio_url,
                'type': 'audio'
            })

            return jsonify({'success': True, 'data': video_data})

    except Exception as e:
        print(f"Error: {str(e)}")
        # Error message ko thoda saaf dikhana
        error_msg = str(e)
        if "Sign in" in error_msg:
            return jsonify({'success': False, 'error': "Server IP Blocked by YouTube (Bot Detection). Try again later."}), 500
        return jsonify({'success': False, 'error': error_msg}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
                    
