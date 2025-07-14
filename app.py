from flask import Flask, request, jsonify
import subprocess
import uuid
import os

app = Flask(__name__)

@app.route('/merge', methods=['POST'])
def merge_audio_video():
    video_url = request.json['video_url']
    audio_url = request.json['audio_url']
    
    # Generate unique filenames
    video_file = f"{uuid.uuid4()}.mp4"
    audio_file = f"{uuid.uuid4()}.wav"
    output_file = f"{uuid.uuid4()}.mp4"
    
    # Download video and audio
    os.system(f"curl -L -o {video_file} {video_url}")
    os.system(f"curl -L -o {audio_file} {audio_url}")
    
    # FFmpeg command with ducking (lower added audio by 10 dB)
    command = (
        f'ffmpeg -y -i {video_file} -i {audio_file} '
        f'-filter_complex "[1:a]volume=0.3162[a1]; [0:a][a1]amix=inputs=2" '
        f'-c:v copy {output_file}'
    )
    
    subprocess.run(command, shell=True)
    
    # Move output to static folder
    os.system(f"mv {output_file} static/{output_file}")

    return jsonify({
        'url': f'https://YOUR_RENDER_URL/static/{output_file}'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

