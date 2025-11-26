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
        # --- SOLUTION: Using Public API (Invidious) ---
        # Ye IP Block problem ko bypass karega
        api_url = f"https://inv.tux.pizza/api/v1/videos/{video_id}"
        
        response = requests.get(api_url, timeout=15)
        
        if response.status_code != 200:
            return jsonify({'error': 'Could not fetch video data. Server busy, try again.'}), 500

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
                if f.get('container') == 'mp4': 
                    video_data['formats'].append({
                        'quality': f.get('qualityLabel', 'HD'),
                        'resolution': f.get('resolution', 'Video'),
                        'size': "Unknown", 
                        'url': f.get('url'),
                        'type': 'video'
                    })

        # Audio Process karna
        if 'adaptiveFormats' in info:
            for f in info['adaptiveFormats']:
                if f.get('type') and 'audio' in f.get('type'):
                    video_data['formats'].append({
                        'quality': 'Audio (MP3)',
                        'resolution': 'Audio Only',
                        'size': "High Quality",
                        'url': f.get('url'),
                        'type': 'audio'
                    })
                    break 

        return jsonify({'success': True, 'data': video_data})

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'success': False, 'error': "Server Error."}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
