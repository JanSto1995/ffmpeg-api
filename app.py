from flask import Flask, request, jsonify
import subprocess
import uuid
import os

app = Flask(__name__)

# Health check endpoint for Render
@app.route('/healthz', methods=['GET'])
def healthz():
    return 'OK', 200

@app.route('/merge', methods=['POST'])
def merge_audio_video():
    video_url = request.json.get('video_url')
    audio_url = request.json.get('audio_url')
    if not video_url or not audio_url:
        return jsonify({'error': 'Please provide video_url and audio_url'}), 400

    # Generate unique filenames
    video_file = f"{uuid.uuid4()}.mp4"
    audio_file = f"{uuid.uuid4()}.wav"
    output_file = f"{uuid.uuid4()}.mp4"

    # Download video and audio
    os.system(f"curl -L -o {video_file} {video_url}")
    os.system(f"curl -L -o {audio_file} {audio_url}")

    # Check if video has an audio stream
    check_audio_cmd = (
        f'ffprobe -loglevel error -select_streams a '
        f'-show_entries stream=codec_type '
        f'-of default=noprint_wrappers=1:nokey=1 {video_file}'
    )
    result = subprocess.run(check_audio_cmd, shell=True, capture_output=True, text=True)
    video_has_audio = bool(result.stdout.strip())

    if video_has_audio:
        # Video has audio → Mix both, duck external audio
        command = (
            f'ffmpeg -y -i {video_file} -i {audio_file} '
            f'-filter_complex "[1:a]volume=0.3162[a1]; [0:a][a1]amix=inputs=2" '
            f'-c:v copy {output_file}'
        )
    else:
        # Video has no audio → Just add external audio
        command = (
            f'ffmpeg -y -i {video_file} -i {audio_file} '
            f'-map 0:v -map 1:a -c:v copy -shortest {output_file}'
        )

    subprocess.run(command, shell=True, check=True)

    # Move output to static folder
    os.makedirs('static', exist_ok=True)
    os.replace(output_file, os.path.join('static', output_file))

    # Construct and return public URL
    render_url = os.getenv('RENDER_EXTERNAL_URL') or 'https://YOUR_RENDER_URL'
    return jsonify({
        'url': f'{render_url}/static/{output_file}'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)

