import os

def extract_audio(video_path, audio_path):
    cmd = f'ffmpeg -i "{video_path}" -q:a 0 -map a "{audio_path}" -y'
    os.system(cmd)

if __name__ == "__main__":
    extract_audio("data/input.mp4", "data/audio.wav")
