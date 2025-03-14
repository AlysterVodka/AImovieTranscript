import whisper_timestamped
import json
import os

model = whisper_timestamped.load_model("base", device="cuda")

def transcribe_audio(audio_path, output_json):
    result = whisper_timestamped.transcribe(model, audio_path)
    transcript = [{"start": s["start"], "end": s["end"], "text": s["text"]} for s in result["segments"]]

    with open(output_json, "w") as f:
        json.dump(transcript, f)

if __name__ == "__main__":
    transcribe_audio("data/audio.wav", "data/transcript.json")

# Controleer of de transcriptie correct is opgeslagen
transcript_path = "data/transcript.json"
if not os.path.exists(transcript_path):
    print("FOUT: transcript.json is niet gegenereerd!")
else:
    with open(transcript_path, "r") as f:
        data = f.read()
        print(f"Transcript.json inhoud:\n{data[:500]}")  # Laat de eerste 500 tekens zien