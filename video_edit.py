import moviepy.editor as mp
import numpy as np
import json
import os
import sys

def find_nearest_zero_crossing(audio_array, start_frame, sample_rate):
    """Zoekt het dichtstbijzijnde nul-crossing punt in de audio."""
    window_size = int(sample_rate * 0.02)  # 20ms marge om een zero-crossing te vinden
    segment = audio_array[start_frame : start_frame + window_size]
    zero_crossings = np.where(np.diff(np.sign(segment)))[0]
    
    if len(zero_crossings) > 0:
        return start_frame + zero_crossings[0]  # Gebruik de eerste zero-crossing
    return start_frame  # Geen zero-crossing gevonden, behoud originele waarde

def adjust_timestamps(timestamps):
    """
    Corrigeert timestamps door zero-crossings te zoeken in data/audio.wav.
    Geeft een lijst van (start, end) terug met de aangepaste waarden.
    """
    adjusted_timestamps = []
    sample_rate = 44100

    # Lees de WAV in (i.p.v. de MP4)
    audio_clip = mp.AudioFileClip("data/audio.wav")

    # Maak soundarray
    audio_array = audio_clip.to_soundarray(fps=sample_rate)
    if audio_array.size == 0:
        print("FOUT: Audio-array is leeg. Controleer data/audio.wav.")
        return timestamps  # Geen aanpassingen mogelijk

    # Mono-kanaal pakken (eerste kolom) als er meerdere zijn
    audio = audio_array[:, 0] if audio_array.ndim > 1 else audio_array

    # Zero-crossings zoeken voor ieder fragment
    for start, end in timestamps:
        start_frame = int(start * sample_rate)
        end_frame   = int(end   * sample_rate)

        start_adj = find_nearest_zero_crossing(audio, start_frame, sample_rate) / sample_rate
        end_adj   = find_nearest_zero_crossing(audio, end_frame,   sample_rate) / sample_rate

        adjusted_timestamps.append((start_adj, end_adj))

    return adjusted_timestamps

def extract_clips(video_path, timestamps_json, output_path):
    # 1. Controleer of timestamps.json bestaat
    if not os.path.exists(timestamps_json):
        print(f"FOUT: {timestamps_json} niet gevonden. Controleer analyse.py.")
        sys.exit(1)

    # 2. Lees timestamps in
    with open(timestamps_json, "r") as f:
        try:
            timestamps = json.load(f)
        except json.JSONDecodeError:
            print(f"FOUT: timestamps.json bevat ongeldige JSON. Controleer analyse.py.")
            sys.exit(1)

    # 3. Controleer of timestamps niet leeg zijn
    if not timestamps or not isinstance(timestamps, list):
        print("FOUT: Geen geldige timestamps gevonden!")
        sys.exit(1)

    # 4. Controleer of de MP4 bestaat
    if not os.path.exists(video_path):
        print(f"FOUT: {video_path} niet gevonden. Controleer of extract_audio.py correct werkte.")
        sys.exit(1)

    # 5. Timestamps sorteren en aanpassen op basis van de WAV
    timestamps.sort()
    timestamps = adjust_timestamps(timestamps)

    # 6. Controleer of er na correctie nog geldige timestamps zijn
    if not timestamps or any(len(ts) != 2 for ts in timestamps):
        print("FOUT: Geen geldige timestamps over na correctie!")
        sys.exit(1)

    # 7. Open de MP4 en maak clips op de aangepaste timestamps
    video = mp.VideoFileClip(video_path)
    clips = []
    for start, end in timestamps:
        if start >= end:
            print(f"Waarschuwing: Ongeldige tijdsperiode ({start} - {end}) overgeslagen.")
            continue
        clips.append(video.subclip(start, end))

    if not clips:
        print("FOUT: Geen bruikbare clips over na filtering!")
        sys.exit(1)

    # 8. Samenvoegen en wegschrijven
    final_video = mp.concatenate_videoclips(clips, method="compose")
    final_video.write_videofile(output_path, codec="libx264", fps=30)

if __name__ == "__main__":
    extract_clips("data/input.mp4", "data/timestamps.json", "data/output.mp4")
