from transformers import WhisperProcessor, WhisperForConditionalGeneration
# KNOWN ISSUE: SIMLINKS DON'T WORK ON WINDOWS
# SOLUTION: populate the pretrained_models folder with a folder called "speechbrain", then download
    # classifier.ckpt, embedding_model.ckpt, hyperparams.yaml, label_encoder.ckpt, mean_var_norm_emb.ckpt
    # these all come from the huggingface model speechbrain/spkrec-ecapa-voxceleb

import os
os.environ["PYANNOTE_CACHE"] = "./pretrained_models"
import librosa
import torch
device = "cuda:0" if torch.cuda.is_available() else "cpu"
from transformers import pipeline
from pyannote.audio import Pipeline
import csv
import pathlib
import torchaudio
import shutil

class Transcriber:
    def __init__(self):
        print("loading audio segmenter")
        self.offline_vad = Pipeline.from_pretrained("pyannote_config.yaml")
        print("loading whisper model")
        self.whisper = pipeline(
            "automatic-speech-recognition",
            model="openai/whisper-medium",
            chunk_length_s=30,
            device=device,
        )
        self.wav_cache = './wave_cache_tmp'
        pathlib.Path(self.wav_cache).mkdir(parents=True, exist_ok=True)
        self.sampling_rate = 16000 #required for whisper

    def _convert_file(self, filename, targetname):
        command = f"ffmpeg -i {filename} -vn -ar {self.sampling_rate} {targetname}"
        os.system(command) #run ffmpeg

    def _load_audio(self, filename):
        # assumes that we are in wave land
        y, sr = torchaudio.load(filename)
        y = torch.mean(y, dim=0)  # reduce to mono
        assert sr == 16000 #should have been done through ffmpeg already
        return y

    def _segment_audio(self, audio_data: torch.Tensor):
        audio_in_memory = {"waveform": torch.unsqueeze(audio_data, dim=0), "sample_rate": self.sampling_rate}
        print("running segmenter!")
        result = self.offline_vad(audio_in_memory)
        segmented_y = []  # speaker to segment + blocks
        for speech_turn, track, speaker in result.itertracks(yield_label=True):
            info_dict = {}
            info_dict["waveform"] = y_resamp[int(speech_turn.start * sampling_rate): int(
                speech_turn.end * sampling_rate)].cpu().numpy()
            info_dict["start"] = speech_turn.start
            info_dict["end"] = speech_turn.end
            info_dict["identity"] = speaker
            segmented_y.append(info_dict)
            # print(f"{speech_turn.start:4.1f} {speech_turn.end:4.1f} {speaker}")
        return segmented_y

    def _transcribe_segments(self, segmented_data):
        transcribed_data = []
        for speech_snippet in segmented_y:
            transcript = self.whisper({"array": speech_snippet["waveform"].copy(), "sampling_rate": sampling_rate}, batch_size=8)["text"]
            current_chunk = [speech_snippet['identity'], round(speech_snippet['start'], 2), round(speech_snippet['end'], 2),
                 transcript]
            # writer.writerow(current_chunk)
            transcribed_data.append(current_chunk)
            print("-------------")
            print(f"{speech_snippet['identity']} {speech_snippet['start']} -- {speech_snippet['end']} \n {transcript}")
        return transcribed_data

    def _save_to_csv(self, transcribed_data, file_name):
        with open(file_name, "w") as f:
            writer = csv.writer(f)
            writer.writerows(transcribed_data)

    def _relabel_speakers(self, transcribed_data, name_dict):
        for data in transcribed_data:
            data[0] = name_dict[data[0]]
        return transcribed_data

    def _save_to_txt(self, transcribed_data, file_name): # for ease of reading
        with open(file_name, "w") as f:
            for data in transcribed_data:
                text = f"{data[0]} {data[1]} -- {data[2]} \n \t {data[3]}"
                f.write(text)

    def _save_to_pdf(self, transcribed_data, file_name):
        # TODO
        pass

    def clear_wav_cache(self):
        shutil.rmtree(self.wav_cache) #deletes this folder
        pathlib.Path(self.wav_cache).mkdir(parents=True, exist_ok=True)

    def process_file(self, filename, out_dir, relabel = False): # relabel is prompted speaker relabeling
        main_name = filename[:filename.rfind(".")]
        target_file = main_name + ".wav"
        self._convert_file(filename, self.wav_cache + "/" + target_file)
        loaded_audio = self._load_audio(self.wav_cache + "/" + target_file)
        segmented_audio = self._segment_audio(loaded_audio)
        transcribed_audio = self._transcribe_segments(segmented_audio)

        # DO RELABELING HERE ##
        if relabel:
            # do some logic: print the transcript, find the speakers
            pass

        ########
        self._save_to_csv(transcribed_audio, out_dir + main_name + ".csv")
        self._save_to_txt(transcribed_audio, out_dir + main_name + ".txt")
        # self._save_to_pdf

transcriber = Transcriber()
transcriber.process_file("behaviortrapmegan.mp3", "./")

quit()
#
# # pipeline = Pipeline.from_pretrained('pyannote/speaker-diarization')
# print("loading pyannote")
# offline_vad = Pipeline.from_pretrained("pyannote_config.yaml")
#
# print("loading file!")
# # y, sr = librosa.load('behaviortrapmegan.mp3')
#
# from pydub import AudioSegment
# # convert wav to mp3
# # import torchaudio
# # os.system("ffmpeg -i behaviortrapmegan.mp3 -vn -ar 16000 behaviortrapmegan.wav")
# y, sr = torchaudio.load("behaviortrapmegan.wav")
# y_resamp = torch.mean(y, dim = 0) #reduce to mono
# y_resamp = y_resamp[0:1920000]
# # y_resamp.to(device)
#
# sampling_rate = 16000
# # y_resamp = librosa.resample(y, orig_sr=sr, target_sr=sampling_rate)
# # y_resamp = y_resamp[0:1920000] # first twom inutes for debugging
# audio_in_memory = {"waveform": torch.unsqueeze(y_resamp, dim = 0), "sample_rate": sampling_rate}
# # audio_in_memory = {"waveform": torch.unsqueeze(torch.tensor(y, device = device), dim = 0), "sample_rate": sampling_rate}
#
# print("running segmenter!")
# result = offline_vad(audio_in_memory)
#
# segmented_y = [] # speaker to segment + blocks
# for speech_turn, track, speaker in result.itertracks(yield_label=True):
#     info_dict = {}
#     info_dict["waveform"] = y_resamp[int(speech_turn.start * sampling_rate) : int(speech_turn.end * sampling_rate)].cpu().numpy()
#     info_dict["start"] = speech_turn.start
#     info_dict["end"] = speech_turn.end
#     info_dict["identity"] =  speaker
#     segmented_y.append(info_dict)
#     # print(f"{speech_turn.start:4.1f} {speech_turn.end:4.1f} {speaker}")
#
#
#
# print("loading whisper")
# pipe = pipeline(
#   "automatic-speech-recognition",
#   model="openai/whisper-medium",
#   chunk_length_s=30,
#   device=device,
# )
#
# with open("test.csv", "w") as f:
#     writer = csv.writer(f)
#
#     for speech_snippet in segmented_y:
#         transcript = pipe({"array" : speech_snippet["waveform"].copy(), "sampling_rate" : sampling_rate}, batch_size=8)["text"]
#         writer.writerow([speech_snippet['identity'], round(speech_snippet['start'], 2), round(speech_snippet['end'], 2), transcript])
#         print("-------------")
#         print(f"{speech_snippet['identity']} {speech_snippet['start']} -- {speech_snippet['end']} \n {transcript}")
#
#
# # we can also return timestamps for the predictions
# # prediction = pipe(sample.copy(), batch_size=8, return_timestamps=True)["chunks"]
# # [{'text': ' Mr. Quilter is the apostle of the middle classes and we are glad to welcome his gospel.',
# #   'timestamp': (0.0, 5.44)}]
