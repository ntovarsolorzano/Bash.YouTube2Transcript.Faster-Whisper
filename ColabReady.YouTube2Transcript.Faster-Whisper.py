#@title Pre-Install
!pip install -q faster-whisper
!pip install -q pytube
!pip install -q pydub
!apt install libcublas11 -y -q
!sudo wget https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -O /usr/local/bin/youtube-dl
!sudo chmod a+rx /usr/local/bin/youtube-dl
!youtube-dl --version


#@title YouTube2Transcript [Auto-upload to Drive]
from google.colab import userdata
userdata.get('HF_TOKEN')

# Save files into Google Drive
save_drive = True

if save_drive:
  from google.colab import drive
  import shutil
  drive.mount('/content/drive/')

from faster_whisper import WhisperModel
import re
import time
import os

# Define the mapping from numbers to model names
models = {
    1: "large-v2",
    2: "medium",
    3: "medium.en",
    4: "small",
    5: "small.en",
    6: "base",
    7: "base.en",
    8: "tiny",
    9: "tiny.en"
}

# Print the options
for number, model in models.items():
    print("(%d) > %s" % (number, model))

while True:
    # Ask the user to pick a number
    user_input = int(input("Please enter a number: "))

    # Get the model name corresponding to the number
    model_name = models.get(user_input)

    if model_name is not None:
        print("Model to be used: %s" % model_name)
        break
    else:
        print("Invalid selection. Please try again.")


model_size = model_name

# Run on GPU with FP16
model = WhisperModel(model_size, device="cuda", compute_type="float16")

# or run on GPU with INT8
# model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
# or run on CPU with INT8
# model = WhisperModel(model_size, device="cpu", compute_type="int8")

url = input("Type the YouTube link: ")
os.environ['URL'] = url
!youtube-dl  -o "audio.%(ext)s" -f 140  $URL
!youtube-dl --get-title $URL
filename = "audio.m4a"

segments, info = model.transcribe(filename, beam_size=5)

print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

# Start time read
start_time = time.time()

def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    if hours > 0:
        return "%d:%02d:%02d h" % (hours, minutes, seconds)
    elif minutes > 0:
        return "%d:%02d min" % (minutes, seconds)
    else:
        return "%.3f s" % seconds

def name_cleaner(name):
    clean_name = re.sub(r'[^\w\-_\. ]', '', name)
    clean_name = re.sub(r'\s+', ' ', clean_name)
    clean_name = clean_name.strip()

    arr = clean_name.split(" ")
    if len(arr) > 5:
        clean_name = arr[0] + "_" +  arr[1] + "_"  + arr[2] + "_"  + arr[3] + "_"  + arr[4] + "_"  + arr[5]
    else:
         pass
    return clean_name

new_filename = name_cleaner(filename)
# Open the files in write mode
with open(f'{new_filename}_segments.txt', 'w') as seg_file, open(f'{new_filename}_text_only.txt', 'w') as text_file:
    for segment in segments:
        # Write the segment to the first file
        seg_file.write("[%.2fs -> %.2fs] %s\n" % (segment.start, segment.end, segment.text))
        # Write only the text to the second file
        text_file.write("%s\n" % segment.text)

        print(f"Progress: {format_time(segment.end)}")

end_time = time.time()

execution_time = end_time - start_time

if execution_time > 60:
    if execution_time > 3600:
        execution_time = execution_time / 3600
        print(f"The program took {execution_time} hours to run.")
    else:
        execution_time = execution_time / 60
        print(f"The program took {execution_time} minutes to run.")
else:
    print(f"The program took {execution_time} seconds to run.")

if save_drive:
  # Copying files into Google Drive
  # Segments
  source_path = f'{new_filename}_segments.txt'
  dest_path = f"/content/drive/My Drive/Colab Notebooks/Transcriptions/{new_filename}_segments.txt"
  shutil.copyfile(source_path, dest_path)
  # Full Text
  source_path = f'{new_filename}_text_only.txt'
  dest_path = f"/content/drive/My Drive/Colab Notebooks/Transcriptions/{new_filename}_text_only.txt"
  shutil.copyfile(source_path, dest_path)
