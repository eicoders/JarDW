from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
import re

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'jar_yt_secure_key'

@app.route('/')
def home():
    return render_template('index.html')

def get_video_id(url):
    """YouTube URL se Video ID nikalne ka function"""
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, url)
    if match:
        return match.group(1)
    return None

@app.route('/api/get-info', methods=['POST'])
def get_video_info():
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    video_id = get_video_id(url)
    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL'}), 400

    try:
        # --- SOLUTION: Using Public API (Invidious) to bypass IP Block ---
        # Ham direct YouTube se nahi, balki Invidious instance se data lenge
        api_url = f"https://inv.tux.pizza/api/v1/videos/{video_id}"
        
        response = requests.get(api_url, timeout=10)
        
        if response.status_code != 200:
            return jsonify({'error': 'Could not fetch video data. Try again.'}), 500

        info = response.json()

        video_data = {
            'title': info.get('title', 'Unknown Title'),
            'thumbnail':  info['videoThumbnails'][0]['url'] if info.get('videoThumbnails') else '',
            'duration': f"{info.get('lengthSeconds', 0) // 60}:{info.get('lengthSeconds', 0) % 60:02d}", 
            'views': info.get('viewCount'),
            'formats': []
        }

        # Formats process karna
        if 'formatStreams' in info:
            for f in info['formatStreams']:
                # Sirf MP4 formats
                if f.get('container') == 'mp4': 
                    video_data['formats'].append({
                        'quality': f.get('qualityLabel', 'HD'),
                        'resolution': f.get('resolution', 'Video'),
                        'size': "Unknown", # API size nahi deta kabhi kabhi
                        'url': f.get('url'),
                        'type': 'video'
                    })

        # Audio Process karna (Adaptive Streams)
        if 'adaptiveFormats' in info:
            for f in info['adaptiveFormats']:
                if f.get('type') and 'audio' in f.get('type'):
                    video_data['formats'].append({
                        'quality': 'Audio (MP3/M4A)',
                        'resolution': 'Audio Only',
                        'size': "High Quality",
                        'url': f.get('url'),
                        'type': 'audio'
                    })
                    break # Sirf ek audio kaafi hai

        return jsonify({'success': True, 'data': video_data})

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'success': False, 'error': "Server Error or API busy."}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
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
                    
