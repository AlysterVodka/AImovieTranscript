import re
import json
import os
import subprocess

# Instellingen
MAX_SENTENCE_LENGTH = 100  # Maximale lengte in tekens van een ondertitelregel
SRT_PATH = "data/subtitles.srt"
AUDIO_PATH = "data/audio.wav"
OUTPUT_VIDEO = "data/final_video.mp4"
INPUT_VIDEO = "data/output.mp4"

def run_whisper():
    """Voert Whisper uit en genereert een SRT-bestand."""
    subprocess.run(["whisper", AUDIO_PATH, "--model", "large", "--output_format", "srt"], check=True)

def correct_grammar(text):
    """Corrigeert grammatica en hoofdletters in ondertitels."""
    # Zet alle ' i ' om naar ' I ' correct gebruik
    text = re.sub(r'\bi\b', 'I', text)
    return text

def split_sentences_on_length(sentences, max_length=MAX_SENTENCE_LENGTH):
    """Splits lange zinnen op, maar alleen op logische plekken."""
    adjusted_sentences = []
    
    for sentence in sentences:
        if len(sentence) <= max_length:
            adjusted_sentences.append(sentence)
            continue

        words = sentence.split()
        split_points = [i for i in range(3, len(words) - 3) if words[i].endswith((".", "?", "!"))]
        
        if not split_points:
            split_points = [len(words) // 2]  # Als er geen split-punten zijn, splitsen in het midden
        
        last_split = 0
        for split in split_points:
            if split - last_split > max_length:
                adjusted_sentences.append(" ".join(words[last_split:split]))
                last_split = split
        
        adjusted_sentences.append(" ".join(words[last_split:]))

    return adjusted_sentences

def process_srt():
    """Verwerkt het SRT-bestand: corrigeert grammatica en past zinnen aan."""
    if not os.path.exists(SRT_PATH):
        print("FOUT: SRT-bestand niet gevonden. Controleer Whisper-output.")
        return

    with open(SRT_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    processed_subtitles = []
    buffer = []
    for line in lines:
        line = line.strip()
        
        if line.isdigit() or "-->" in line:
            if buffer:
                corrected_sentence = correct_grammar(" ".join(buffer))
                split_sentences = split_sentences_on_length([corrected_sentence])
                processed_subtitles.extend(split_sentences)
                buffer = []
            processed_subtitles.append(line)
        elif line:
            buffer.append(line)
    
    if buffer:
        corrected_sentence = correct_grammar(" ".join(buffer))
        split_sentences = split_sentences_on_length([corrected_sentence])
        processed_subtitles.extend(split_sentences)

    with open(SRT_PATH, "w", encoding="utf-8") as f:
        for idx, line in enumerate(processed_subtitles, 1):
            if "-->" in line:
                f.write(f"{line}\n")
            else:
                f.write(f"{idx}\n{line}\n\n")

def add_subtitles_to_video():
    """Voegt ondertitels toe aan de video met FFmpeg."""
    if not os.path.exists(INPUT_VIDEO):
        print("FOUT: Video niet gevonden. Controleer output van video_edit.py.")
        return
    
    subprocess.run([
        "ffmpeg",
        "-i", INPUT_VIDEO,
        "-vf", f"subtitles={SRT_PATH}",
        "-c:a", "copy",
        OUTPUT_VIDEO
    ], check=True)

if __name__ == "__main__":
    print("🔹 Whisper wordt uitgevoerd om ondertitels te genereren...")
    run_whisper()
    
    print("🔹 Ondertitels worden verwerkt...")
    process_srt()
    
    print("🔹 Ondertitels worden aan de video toegevoegd...")
    add_subtitles_to_video()
    
    print("✅ Video met ondertitels is gegenereerd.")
