import speech_recognition as sr
from pydub import AudioSegment, silence
import zipfile
import os
import librosa
from mutagen.mp3 import MP3
#Code that splits audio into small chunks below

# Function to split audio on silence
def split_on_silence_with_pydub(audio_segment, min_silence_len=500, silence_thresh=-40):
    """
    audio_segment: the initial audio segment
    min_silence_len: (in ms) minimum length of a silence to be used for splitting
    silence_thresh: (in dB) anything quieter than this will be considered silence
    """
    return silence.split_on_silence(
        audio_segment,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh
    )

# Function to enforce maximum length on audio chunks
def enforce_max_length(chunks, max_length=6000):
    enforced_chunks = []
    for chunk in chunks:
        if len(chunk) <= max_length:
            enforced_chunks.append(chunk)
        else:
            for i in range(0, len(chunk), max_length):
                part = chunk[i:i + max_length]
                enforced_chunks.append(part)
    return enforced_chunks

# Load the audio file
audio_segment = AudioSegment.from_file('ukr1.wav')

# Split the audio into chunks where silence is detected
chunks = split_on_silence_with_pydub(audio_segment, min_silence_len=500, silence_thresh=-40)

# Enforce the maximum length of 6 seconds (6000 ms)
chunks = enforce_max_length(chunks, max_length=6000)

# Save the chunks into individual WAV files
enforced_split_audio_paths = []
for i, chunk in enumerate(chunks):
    chunk_path = f'word/ukr1_enforced_chunk{i}.wav'
    chunk.export(chunk_path, format="wav")
    enforced_split_audio_paths.append(chunk_path)

# Create a zip file containing all the chunks
enforced_zip_path = 'word/ukr1_enforced_chunks.zip'
with zipfile.ZipFile(enforced_zip_path, 'w') as myzip:
    for file in enforced_split_audio_paths:
        myzip.write(file, os.path.basename(file))


#Code that transcribes all the audio chunks below

# Initialize recognizer class (for recognizing the speech)
r = sr.Recognizer()

def transcribe_wav_to_txt(input_zip_file, output_folder, lang='uk-UA'):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Open the ZIP file
    with zipfile.ZipFile(input_zip_file, 'r') as zip_file:
        # Extract all WAV files from the ZIP file
        wav_files = [f for f in zip_file.namelist() if f.lower().endswith('.wav')]

        for wav_file in wav_files:
            # Extract the WAV file
            zip_file.extract(wav_file, path=output_folder)

            # Transcribe the extracted WAV file
            wav_path = os.path.join(output_folder, wav_file)
            with sr.AudioFile(wav_path) as source:
                print('Transcribing', wav_file)
                audio_text = r.listen(source)
                try:
                    text = r.recognize_google(audio_text, language=lang)
                    txt_file = os.path.splitext(wav_file)[0] + '.txt'
                    txt_path = os.path.join(output_folder, txt_file)
                    with open(txt_path, 'w', encoding='utf-8') as txt_file:
                        txt_file.write(text)
                    print('Transcription saved to', txt_path)
                except sr.UnknownValueError:
                    print('Could not transcribe', wav_file)
                except Exception as e:
                    print('Error transcribing', wav_file, e)

if __name__ == "__main__":
    input_zip_file = 'chunks.zip'  
    output_folder = 'transcriptions1'
    transcribe_wav_to_txt(input_zip_file, output_folder)

#Code that combines all transcriptions parts into one text file below.

# Specify the directory containing your text files
directory = 'transcriptions'

# Specify the name of the output file
output_file = 'combined_output.txt'

# Get a list of all text files in the specified directory
text_files = [filename for filename in os.listdir(directory) if filename.endswith('.txt')]

# Sort the list of text files based on the last number in the file name
text_files.sort(key=lambda x: int(''.join(filter(str.isdigit, x))))

# Create or overwrite the output file
with open(output_file, 'w', encoding='utf-8') as outfile:
    # Iterate over sorted files in the specified directory
    for filename in text_files:
        file_path = os.path.join(directory, filename)
        with open(file_path, 'r', encoding='utf-8') as infile:
            outfile.write(infile.read() + ' ')  # Write contents to the output file

print(f"All text files have been combined into {output_file}")

import string

def read_file(file_path):
    """Reads a file and returns a set of words in the file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
        # Removes punctuation and converts to lowercase
        translator = str.maketrans('', '', string.punctuation)
        text = text.translate(translator).lower()
        words = set(text.split())
    return words

def is_one_letter_difference(word1, word2):
    """Checks if there is only a one-letter difference between two words."""
    return len(word1) == len(word2) and sum(a != b for a, b in zip(word1, word2)) == 1 or 2

def calculate_similarity(file1, file2):
    """Calculates the percentage similarity between two sets of words."""
    words1 = read_file(file1)
    words2 = read_file(file2)

    common_words = set()
    for word1 in words1:
        for word2 in words2:
            if word1 == word2 or (len(word1) > 2 and len(word2) > 2 and is_one_letter_difference(word1, word2)):
                common_words.add(word1)
                common_words.add(word2)

    total_words = words1.union(words2)

    if not total_words:
        return 0

    similarity = len(common_words) / len(total_words) * 100
    return similarity

file2_path = 'original_text.txt'
file1_path = 'combined_output.txt'

similarity_percentage = calculate_similarity(file1_path, file2_path)
print(f"The similarity between the files is {similarity_percentage:.2f}%")

#Metadata code below

# Import other necessary libraries or define functions for advanced voice analysis

# Function to extract basic metadata from MP3 file
def get_metadata(mp3_file_path):
    audio = MP3(mp3_file_path)
    metadata = {
        "Title": audio.get('TIT2'),
        "Artist": audio.get('TPE1'),
        "Album": audio.get('TALB'),
        "Track Number": audio.get('TRCK'),
        "Year": audio.get('TDRC'),
        "Length": audio.info.length
    }
    return metadata

# Function to analyze voice properties (placeholder functionality)
def analyze_voice_properties(audio_file_path):
    # Load audio file
    audio, sample_rate = librosa.load(audio_file_path)

    # Dummy placeholders for actual analysis
    age = "32"  # Replace with actual age detection logic
    gender = "Male"  # Replace with actual gender detection logic
    accent = "Ukranian"  # Replace with actual accent detection logic

    return {
        "Age": age,
        "Gender": gender,
        "Accent": accent
    }

# Function to write combined results to a file
def write_to_file(metadata, analysis, file_path):
    with open(file_path, 'w') as file:
        for key, value in metadata.items():
            file.write(f"{key}: {value}\n")
        for key, value in analysis.items():
            file.write(f"{key}: {value}\n")

# Main execution
if __name__ == "__main__":
    mp3_file_path = 'ukr1.mp3'  # Replace with the path to your MP3 file
    metadata = get_metadata(mp3_file_path)
    voice_analysis = analyze_voice_properties(mp3_file_path)
    write_to_file(metadata, voice_analysis, 'metadata.txt')

