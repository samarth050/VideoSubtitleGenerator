from faster_whisper import WhisperModel

print("Loading model...")

model = WhisperModel(
    "base",
    device="cpu"
)
segments, info = model.transcribe(
    r"D:\Movies\Asian.mp4",
    task="translate",
    beam_size=5
)
#segments, info = model.transcribe(
#    r"D:\Movies\Asian.mp4"
#)

print(f"Detected Language: {info.language}")

for segment in segments:
    print(
        f"[{segment.start:.2f} -> {segment.end:.2f}] "
        f"{segment.text}"
    )