import os
import sys
import psutil
import time

SCRIPTS = ["extract_audio.py", "transcribe.py", "analyse.py", "video_edit.py", "add_subtitles.py"]
LOCKFILE = "script_running.lock"

def beëindig_bestaande_processen():
    """Zoekt en stopt actieve instanties van de scripts."""
    huidige_pid = os.getpid()

    for proces in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            cmdline = " ".join(proces.info["cmdline"]) if proces.info["cmdline"] else ""
            if any(script in cmdline for script in SCRIPTS) and proces.info["pid"] != huidige_pid:
                print(f"Beëindig proces {proces.info['pid']} ({cmdline})")
                proces.terminate()  # Probeer het netjes te stoppen
                time.sleep(1)  # Geef het even de tijd om af te sluiten
                if proces.is_running():
                    proces.kill()  # Forceer als het niet stopt
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

def maak_lockbestand():
    """Maakt een lockbestand aan om te voorkomen dat meerdere instanties draaien."""
    with open(LOCKFILE, "w") as f:
        f.write(str(os.getpid()))

def verwijder_lockbestand():
    """Verwijdert het lockbestand zodra het script klaar is."""
    if os.path.exists(LOCKFILE):
        os.remove(LOCKFILE)

# Zoek en stop alle lopende processen van de scripts
beëindig_bestaande_processen()

# Maak een lock om te voorkomen dat meerdere instanties tegelijk draaien
maak_lockbestand()

try:
    print("Script gestart...")

    # Stap 1: Extraheer audio
    os.system("python extract_audio.py")

    # Stap 2: Transcribeer audio naar tekst (toegevoegd!)
    os.system("python transcribe.py")  

    # Stap 3: Analyseer transcriptie en genereer timestamps
    os.system("python analyse.py")

    # Stap 4: Knip en bewerk video
    os.system("python video_edit.py")

    # Stap 5: Voeg ondertitels toe
    os.system("python add_subtitles.py")

    print("Script voltooid.")
finally:
    verwijder_lockbestand()  # Zorgt ervoor dat de lock wordt verwijderd, zelfs bij een crash
