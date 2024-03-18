import os
import wave
import numpy as np

def combine_wav_files(root_directory):
    
    for root, dirs, files in os.walk(root_directory):
        
        wave_files = [file for file in files if file.endswith(".wav")]

        if len(wave_files) > 1:
            
            wave_files.sort()

            first_wave_file = wave.open(os.path.join(root, wave_files[0]), 'rb')
            params = first_wave_file.getparams()

            output_file_name = "_".join([os.path.splitext(file)[0] for file in wave_files]) + ".wav"
            output_file_path = os.path.join(root, output_file_name)
            output_wave = wave.open(output_file_path, 'wb')
            output_wave.setparams(params)

            for i, file_name in enumerate(wave_files):
                with wave.open(os.path.join(root, file_name), 'rb') as wave_file:
                    data = wave_file.readframes(wave_file.getnframes())
                    output_wave.writeframes(data)
                
                if i < len(wave_files) - 1:
                    silence_frames = np.zeros(params.nchannels * params.sampwidth * params.framerate, dtype=np.uint8)
                    output_wave.writeframes(silence_frames.tobytes())

            output_wave.close()
            first_wave_file.close()

            print(f"Combined {len(wave_files)} wave files into {output_file_path}")

if __name__ == "__main__":
    root_directory = input("Enter top-level directory: ")

    combine_wav_files(root_directory)
