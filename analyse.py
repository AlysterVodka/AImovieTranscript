import json
import torch
import os
import sys
import re
from transformers import AutoModelForCausalLM, AutoTokenizer

# Model laden
model_name = "deepseek-ai/deepseek-llm-7b-chat"
device = "cuda" if torch.cuda.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto", torch_dtype=torch.float16)

def analyse_transcript(transcript_json, output_json):
    # Controleer of transcript.json bestaat
    if not os.path.exists(transcript_json):
        print(f"FOUT: {transcript_json} bestaat niet. Controleer transcribe.py.")
        sys.exit(1)

    # Laad transcriptie
    with open(transcript_json, "r") as f:
        try:
            transcript = json.load(f)
        except json.JSONDecodeError:
            print(f"FOUT: transcript.json bevat ongeldige JSON. Controleer transcribe.py.")
            sys.exit(1)

    if not transcript:
        print("FOUT: transcript.json is leeg. Analyse wordt afgebroken.")
        sys.exit(1)

    # Combineer transcript naar één lange tekst
    full_text = "\n".join([seg["text"] for seg in transcript])

    # AI-prompt
    prompt = f"""
    Hier is een volledige transcriptie van een video:

    {full_text}

    1. Bepaal het **hoofdonderwerp** van deze transcriptie.
    2. Selecteer fragmenten die:
       - Het meest **interessant** of **grappig** zijn.
       - Het **beste aansluiten bij het hoofdonderwerp**.
       - **Logisch in elkaar overlopen**, zodat de kijker begrijpt hoe fragmenten verbonden zijn.
    3. **Behoud de originele volgorde van de transcriptie.**
    4. **Knip nooit een zin halverwege af**. Elk fragment moet een volledige, afgeronde zin bevatten.
    5. Zorg ervoor dat de totale duur **maximaal 90 seconden** is.
    6. **Geef de output als een geldige JSON-lijst** met alleen de begin- en eindtijden van de geselecteerde fragmenten.

    Voorbeeld output:
    ```json
    [[0, 12], [45, 60], [85, 100]]
    ```
    """

    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    output = model.generate(**inputs, max_new_tokens=300)

    # Decoderen van AI-output
    response_text = tokenizer.decode(output[0], skip_special_tokens=True)

    # Zoek JSON-lijst in de AI-output
    json_match = re.search(r"\[\[.*?\]\]", response_text, re.DOTALL)
    if json_match:
        try:
            selected_segments = json.loads(json_match.group(0))
        except json.JSONDecodeError:
            print("FOUT: AI-output kon niet worden omgezet naar geldige JSON. Dit is de ruwe output:")
            print(response_text)
            sys.exit(1)
    else:
        print("FOUT: Geen JSON-output gevonden in AI-respons.")
        print(response_text)
        sys.exit(1)

    # Controleer of er segmenten zijn
    if not selected_segments or not isinstance(selected_segments, list):
        print("FOUT: AI heeft geen timestamps geselecteerd.")
        sys.exit(1)

    # Opslaan naar timestamps.json
    with open(output_json, "w") as f:
        json.dump(selected_segments, f)

    print(f"timestamps.json succesvol gegenereerd: {output_json}")

if __name__ == "__main__":
    analyse_transcript("data/transcript.json", "data/timestamps.json")

# debug
# Controleer of transcript.json bestaat
transcript_path = "data/transcript.json"
if not os.path.exists(transcript_path):
    print("FOUT: transcript.json bestaat niet. Controleer transcribe.py.")
    exit(1)

# Laad de transcriptie
with open(transcript_path, "r") as f:
    try:
        transcript = json.load(f)
    except json.JSONDecodeError:
        print("FOUT: transcript.json bevat ongeldige JSON.")
        exit(1)

if not transcript:
    print("FOUT: transcript.json is leeg! Controleer transcribe.py.")
    exit(1)

# Debug: print de eerste paar transcriptregels
print(f"Eerste regels transcript.json:\n{transcript[:3]}")

# Controleer of timestamps correct worden gegenereerd
timestamps_path = "data/timestamps.json"
if not os.path.exists(timestamps_path):
    print("FOUT: timestamps.json is niet gegenereerd!")
    exit(1)
else:
    with open(timestamps_path, "r") as f:
        timestamps_data = f.read()
        print(f"Timestamps.json inhoud:\n{timestamps_data[:500]}")  # Debug-output