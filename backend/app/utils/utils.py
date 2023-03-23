def validate_format(ext: str):
    formats = ["wav", "opus", "webm", "m4a", "mp4"]
    return ext in formats
