import re
import json
import os
import subprocess

# Instellingen
MAX_SENTENCE_LENGTH = 50  # Maximale lengte in tekens per ondertitelregel
MIN_SENTENCE_LENGTH = 20   # Minimale lengte per regel voordat er een nieuwe regel wordt afgedwongen
SRT_PATH = "data/subtitles.srt"  # Zorg dat de ondertitels in de juiste map blijven
AUDIO_PATH = "data/audio.wav"
OUTPUT_VIDEO = "data/final_video.mp4"
INPUT_VIDEO = "data/output.mp4"

def run_whisper():
    """Voert Whisper uit en genereert een SRT-bestand in de juiste map."""
    subprocess.run([
        "whisper", AUDIO_PATH, "--model", "large", "--output_format", "srt", "--output_dir", "data"
    ], check=True)

def correct_grammar(text):
    """Corrigeert grammatica en hoofdletters in ondertitels."""
    # Maak gebruik van een regex om alle relevante woorden te vervangen
    corrections = {
        r'\bi\b': 'I',
        r"\bi'm\b": "I'm",
        r"\bi've\b": "I've",
        r"\bi'd\b": "I'd",
        r"\bi'll\b": "I'll"
    }
    for pattern, replacement in corrections.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def determine_break_symbol(sentence, next_sentence):
    """Bepaalt welk leesteken gebruikt moet worden bij het afbreken van de zin."""
    if sentence.endswith(("!", "?")):
        return " "  # Geen extra leesteken nodig
    if next_sentence.startswith(("because", "so", "therefore", "thus")):
        return ":"  # Dubbele punt als de volgende zin een verklaring of gevolg is
    if len(next_sentence.split()) < 5:
        return " —"  # Afbreekstreepje als de volgende zin kort is
    return ","  # Standaard: een komma als de zin doorloopt

def split_sentences_on_length(sentences, max_length=MAX_SENTENCE_LENGTH, min_length=MIN_SENTENCE_LENGTH):
    """Splits lange zinnen op, maar alleen op logische plekken."""
    adjusted_sentences = []
    
    for i, sentence in enumerate(sentences):
        if len(sentence) <= max_length:
            adjusted_sentences.append(sentence)
            continue

        words = sentence.split()
        split_points = [idx for idx in range(3, len(words) - 3) if words[idx].endswith((".", "?", "!"))]
        
        if not split_points:
            split_points = [len(words) // 2]  # Als er geen split-punten zijn, splits in het midden
        
        last_split = 0
        for split in split_points:
            if split - last_split > min_length:
                next_sentence = " ".join(words[split:])
                adjusted_sentences.append(" ".join(words[last_split:split]) + determine_break_symbol(words[last_split:split], next_sentence))
                last_split = split

        adjusted_sentences.append(" ".join(words[last_split:]))

    return adjusted_sentences

def process_srt():
    """Verwerkt het SRT-bestand: corrigeert grammatica en past zinnen aan."""
    if not os.path.exists(SRT_PATH):
        print(f"FOUT: {SRT_PATH} niet gevonden. Controleer Whisper-output.")
        return

    with open(SRT_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    processed_subtitles = []
    buffer = []
    previous_speaker = None

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
            if "Speaker" in line and line != previous_speaker:
                buffer.append(f'"{line}"')  # Gebruik aanhalingstekens bij nieuwe sprekers
                previous_speaker = line
            else:
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
    print("Whisper wordt uitgevoerd om ondertitels te genereren...")
    run_whisper()
    
    print("Ondertitels worden verwerkt...")
    process_srt()
    
    print("Ondertitels worden aan de video toegevoegd...")
    add_subtitles_to_video()
    
    print("Video met ondertitels is gegenereerd.")
