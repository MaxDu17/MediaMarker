from transformers import WhisperProcessor, WhisperForConditionalGeneration
import librosa
import torch
device = "cuda:0" if torch.cuda.is_available() else "cpu"

# processor = WhisperProcessor.from_pretrained("openai/whisper-large")
# model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-large").to(device)
# # model.config.forced_decoder_ids = WhisperProcessor.get_decoder_prompt_ids(language="english", task="transcribe")
# model.config.forced_decoder_ids = None

import os
os.environ["PYANNOTE_CACHE"] = "./pretrained_models"

from pyannote.audio import Pipeline


import torchaudio
# from speechbrain.pretrained import EncoderClassifier
#
# classifier = EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb")
# import ipdb
# ipdb.set_trace()


# pipeline = Pipeline.from_pretrained('pyannote/speaker-diarization')
print("loading pyannote")
offline_vad = Pipeline.from_pretrained("pyannote_config.yaml")
print("done with model!")

y, sr = librosa.load('behaviortrapmegan.mp3')
print("resampling!")
sampling_rate = 16000
y_resamp = librosa.resample(y, orig_sr=sr, target_sr=sampling_rate)

y_resamp = y_resamp[0:1920000] # first twom inutes for debugging

audio_in_memory = {"waveform": torch.unsqueeze(torch.tensor(y_resamp, device = device), dim = 0), "sample_rate": sampling_rate}
result = offline_vad(audio_in_memory)

segmented_y = [] # speaker to segment + blocks

for speech_turn, track, speaker in result.itertracks(yield_label=True):
    info_dict = {}
    info_dict["waveform"] = segmented_y[int(speech_turn.start * sampling_rate) : int(speech_turn.end * sampling_rate)]
    info_dict["start"] = speech_turn.start
    info_dict["end"] = speech_turn.end
    info_dict["identity"] =  speaker
    segmented_y.append(info_dict)
    print(f"{speech_turn.start:4.1f} {speech_turn.end:4.1f} {speaker}")

# input_features = processor(y_resamp, sampling_rate=16000, return_tensors="pt").input_features.to(device)
# # generate token ids
# predicted_ids = model.generate(input_features)
# # transcription = processor.batch_decode(predicted_ids, skip_special_tokens=False)
#
# transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)


print("loading whisper")
from transformers import pipeline
pipe = pipeline(
  "automatic-speech-recognition",
  model="openai/whisper-medium",
  chunk_length_s=30,
  device=device,
)

# ds = load_dataset("hf-internal-testing/librispeech_asr_dummy", "clean", split="validation")
# sample = ds[0]["audio"]

for speech_snippet in segmented_y:
  transcript = pipe({"array" : speech_snippet["waveform"].copy(), "sampling_rate" : sampling_rate}, batch_size=8)["text"]
  print("-------------")
  print(f"{speech_snippet['identity']} {speech_snippet['start']} -- {speech_snippet['end']} \n {transcript}")

# prediction = pipe({"array" : y_resamp.copy(), "sampling_rate" : sampling_rate}, batch_size=8)["text"]

# https://github.com/openai/whisper/discussions/264 TO LABEL SPEAKERS
# https://lablab.ai/t/whisper-transcription-and-speaker-identification


# " Mr. Quilter is the apostle of the middle classes, and we are glad to welcome his gospel."

# we can also return timestamps for the predictions
# prediction = pipe(sample.copy(), batch_size=8, return_timestamps=True)["chunks"]
# [{'text': ' Mr. Quilter is the apostle of the middle classes and we are glad to welcome his gospel.',
#   'timestamp': (0.0, 5.44)}]
