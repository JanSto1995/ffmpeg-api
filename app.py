from flask import Flask, request, jsonify
import subprocess
import uuid
import os

app = Flask(__name__)

@app.route('/merge', methods=['POST'])
def merge_audio_video():
    video_url = request.json['video_url']
    audio_url = request.json['audio_url']
    
    video_file = f"{uuid.uuid4()}.mp4"
    audio_file = f"{uuid.uuid4()}.wav"
    output_file = f"{uuid.uuid4()}.mp4"
    
    os.system(f"curl -L -o {video_file} {video_url}")
    os.system(f"curl -L -o {audio_file} {audio_url}")
    
    command = f'ffmpeg -y -i {video_file} -i {audio_file} -filter_complex "[0:a][1:a]amix=inputs=2" -c:v copy {output_file}'
    subprocess.run(command, shell=True)
    
    os.system(f"mv {output_file} static/{output_file}")

    return jsonify({
        'url': f'https://YOUR_RENDER_URL/static/{output_file}'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

