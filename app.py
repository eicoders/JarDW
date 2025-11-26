from flask import Flask, render_template, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

# --- CONFIGURATION ---
# Personal Use ke liye simple rakhte hain
app.config['SECRET_KEY'] = 'jar_yt_secure_key'

# --- ROUTES ---

@app.route('/')
def home():
    """HTML Page load karega"""
    return render_template('index.html')

@app.route('/api/get-info', methods=['POST'])
def get_video_info():
    """
    Frontend se URL lega aur yt-dlp ka use karke
    Title, Thumbnail aur Formats return karega.
    """
    data = request.json
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        # yt-dlp options (Tezi se info lane ke liye)
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'best', # Best quality by default
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Video ki jaankari nikalna (Download nahi karega, sirf info layega)
            info = ydl.extract_info(url, download=False)

            # Data ko clean karke Frontend ke liye ready karna
            video_data = {
                'title': info.get('title', 'Unknown Title'),
                'thumbnail': info.get('thumbnail'),
                'duration': info.get('duration_string'), # e.g. "10:05"
                'views': info.get('view_count'),
                'formats': []
            }

            # Formats filter karna (Hame sirf MP4 aur MP3 chahiye)
            for f in info['formats']:
                # Note: Youtube ke direct URLs kuch der baad expire ho jate hain
                # Isliye ye temporary direct links hain.
                
                # Sirf wo formats lo jo MP4 hon aur jinme Video+Audio dono ho (best experience)
                if f.get('ext') == 'mp4' and f.get('acodec') != 'none' and f.get('vcodec') != 'none':
                    filesize = f.get('filesize', 0)
                    if filesize:
                        filesize_mb = round(filesize / (1024 * 1024), 1) # Convert to MB
                    else:
                        filesize_mb = "Unknown"
                    
                    video_data['formats'].append({
                        'quality': f.get('format_note', 'HD'),
                        'resolution': f.get('resolution'),
                        'size': f"{filesize_mb} MB",
                        'url': f.get('url'), # Direct Download Link
                        'type': 'video'
                    })

            # Best Audio Format dhoondhna
            video_data['formats'].append({
                'quality': 'High (MP3)',
                'resolution': 'Audio Only',
                'size': 'N/A',
                'url':  next((f['url'] for f in info['formats'] if f.get('acodec') != 'none' and f.get('vcodec') == 'none'), '#'),
                'type': 'audio'
            })

            return jsonify({'success': True, 'data': video_data})

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Debug mode on rakha hai taaki errors dikh sakein
    app.run(debug=True, port=5000)
