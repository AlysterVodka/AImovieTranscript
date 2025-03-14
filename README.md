Scripts om video snippets in te lezen en automatisch te editen voor een korter filmpje [reel/short].
Werkt alleen om ondertitels te genereren op het moment.

### Structuur

| /Main folder |
|- main.py                    |  # Hoofdscript dat alles start |
|- extract_audio.py           |  # Haalt audio uit de video |
|- transcribe.py              |  # Zet audio om in tekst |
|- analyze.py                 |  # Bepaalt de belangrijkste stukken | 
|- video_edit.py              |  # Knipt de video | 
|- add_subtitles.py           |  # Voegt ondertitels toe | 
|- data/ |
|    -   input.mp4            |   # De originele video | 
|    -   timestamps.json      |   # Belangrijke tijdstempels (wordt automatisch gegenereerd) |
|    -   output.mp4           |   # De bewerkte video |

input file moet dus input.mp4 heten en in 'data' staan.

#### Installeren in terminal via pip:
- versie van moviepy onder 2.0 [numpy 1.26.4]
- optimum
- torch transformers sentence-transformers accelerate
- pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
- pip install auto-gptq [AI model]
- pip install imageio[ffmpeg]
- numpy scipy
- openai-whisper OF whisperx [voor CUDA, niet getest]
- pip install transformers huggingface_hub

ffmpeg ook downloaden van website: https://www.gyan.dev/ffmpeg/builds/
- git-essentials.7z

#CUDA toolkit van NVIDIA
https://developer.nvidia.com/cuda-downloads?target_os=Windows&target_arch=x86_64&target_version=10&target_type=exe_network

