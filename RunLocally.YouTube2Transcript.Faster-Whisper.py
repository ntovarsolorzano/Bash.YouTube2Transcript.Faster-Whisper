

#@title Faster-Whisper [YouTube]

# PART 1 - REQUESTS A YOUTUBE LINK ---------------------------------------------

from faster_whisper import WhisperModel
import re
import time
from pytube import YouTube
import re
from pydub import AudioSegment
import os

def find_latest_file(prefix, path='.'):
    # Find files that match the prefix
    files = [f for f in os.listdir(path) if f.startswith(prefix)]

    # Check if any matching files were found
    if not files:
        return None

    # Find the most recently created file
    latest_file = max(files, key=lambda f: os.path.getmtime(os.path.join(path, f)))

    return latest_file

def audio_duration(file_path):
    audio = AudioSegment.from_file(file_path)
    total_seconds = audio.duration_seconds

    # Convert to hours, minutes, seconds
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = total_seconds % 60

    # Build the output string
    duration_str = "Audio duration is: "
    if hours > 0:
        duration_str += f"{hours} hours, "
    if minutes > 0:
        duration_str += f"{minutes} min, "
    duration_str += f"{int(seconds)} seconds"

    return duration_str

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

def download_video_and_audio(link):
    yt = YouTube(link)

    # download audio
    audio_stream = yt.streams.filter(only_audio=True).first()
    if audio_stream is not None:
        audio_filename = name_cleaner(audio_stream.default_filename)
        audio_filename = "audio_" + audio_filename + ".mp3"
        audio_stream.download(filename=audio_filename)
        print("Audio filename: ", audio_stream.default_filename)
        print(f"To be recorded as: {audio_filename}")

link = input("Enter the YouTube link: ")


# PART 2: TRANSLATE THAT AUDIO --------------------------------------------------

#@title Run | Asks for models [Runs on a YouTube audio] / Runs First Box No.1.
# Github: https://github.com/SYSTRAN/faster-whisper


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
print("Now select a model:")
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

# Get the YouTube audio
download_video_and_audio(link)

# Use the function to find the audio file
latest_audio = find_latest_file('audio_')
print("Transcribing audio file:", latest_audio)

# Use the function to print audio length
duration = audio_duration(latest_audio)
print(duration)

filename = latest_audio
segments, info = model.transcribe(filename, beam_size=5)

print("Detected language '%s' with probability %f" % (info.language, info.language_probability))

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

# Record the start time
start_time = time.time()

new_filename = "transcript_" + name_cleaner(filename)[6:]

# Open the files in write mode
with open(f'{new_filename}_segments.txt', 'w') as seg_file, open(f'{new_filename}_text_only.txt', 'w') as text_file:
    for segment in segments:
        # Write the segment to the first file
        seg_file.write("[%.2fs -> %.2fs] %s\n" % (segment.start, segment.end, segment.text))
        # Write only the text to the second file
        text_file.write("%s\n" % segment.text)

        print(f"Progress: {format_time(segment.end)}")

# Record the end time
end_time = time.time()

# Calculate the elapsed time in seconds
elapsed_time_seconds = end_time - start_time

total_seconds = elapsed_time_seconds

# Convert to hours, minutes, seconds
hours = int(total_seconds // 3600)
minutes = int((total_seconds % 3600) // 60)
seconds = total_seconds % 60

# Build the output string
duration_str = "\nElapsed Time: "
if hours > 0:
    duration_str += f"{hours} hours, "
if minutes > 0:
    duration_str += f"{minutes} min, "
duration_str += f"{int(seconds)} seconds"

print(duration_str)
