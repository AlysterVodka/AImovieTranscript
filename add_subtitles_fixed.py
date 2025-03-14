import re
import os
import subprocess

# Instellingen
MAX_CHAR_LENGTH = 60  # Maximale lengte van een ondertitelregel
AUDIO_PATH = "data/audio.wav"
SRT_PATH = "data/subtitles.srt"

def run_whisper():
    """Voert Whisper uit en genereert een SRT-bestand."""
    subprocess.run([
        "whisper", AUDIO_PATH, "--model", "large", "--output_format", "srt", "--output_dir", "data"
    ], check=True)

def correct_grammar(text):
    """Corrigeert grammatica, interpunctie en hoofdletters."""
    corrections = {
        r'\bi\b': 'I',
        r"\bi'm\b": "I'm",
        r"\bi've\b": "I've",
        r"\bi'd\b": "I'd",
        r"\bi'll\b": "I'll"
    }
    for pattern, replacement in corrections.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    # Hoofdletters en interpunctie corrigeren
    sentences = re.split(r"([.!?])\s*", text)
    corrected_sentences = []
    capitalize_next = True

    for part in sentences:
        if part in ".!?":
            corrected_sentences.append(part)
            capitalize_next = True
        else:
            if capitalize_next and part:
                corrected_sentences.append(part.capitalize())
            else:
                corrected_sentences.append(part)
            capitalize_next = False

    return "".join(corrected_sentences)

def split_long_sentences(text):
    """Splits te lange ondertitelregels op maximaal 60 karakters."""
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + 1 <= MAX_CHAR_LENGTH:
            current_line += " " + word if current_line else word
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines

def process_srt():
    """Leest, corrigeert en herformatteert de SRT-bestand output."""
    if not os.path.exists(SRT_PATH):
        print(f"FOUT: {SRT_PATH} niet gevonden. Controleer Whisper-output.")
        return

    with open(SRT_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    processed_subtitles = []
    buffer = []
    current_timestamp = None
    index = 1

    for line in lines:
        line = line.strip()
        
        if "-->" in line:
            if buffer and current_timestamp:
                corrected_sentence = correct_grammar(" ".join(buffer))
                split_sentences = split_long_sentences(corrected_sentence)
                for sentence in split_sentences:
                    processed_subtitles.append(f"{index}\n{current_timestamp}\n{sentence}\n")
                    index += 1
                buffer = []
            current_timestamp = line
        elif line.isdigit():
            continue  # Ondertitel index overslaan
        elif line:
            buffer.append(line)
        else:
            continue  # Lege regel overslaan

    if buffer and current_timestamp:
        corrected_sentence = correct_grammar(" ".join(buffer))
        split_sentences = split_long_sentences(corrected_sentence)
        for sentence in split_sentences:
            processed_subtitles.append(f"{index}\n{current_timestamp}\n{sentence}\n")
            index += 1

    with open(SRT_PATH, "w", encoding="utf-8") as f:
        f.writelines("\n".join(processed_subtitles))

if __name__ == "__main__":
    print("Whisper wordt uitgevoerd om ondertitels te genereren...")
    run_whisper()
    
    print("Ondertitels worden verwerkt en gecorrigeerd...")
    process_srt()
    
    print(f"Ondertitels succesvol gegenereerd en gecorrigeerd in {SRT_PATH}.")
