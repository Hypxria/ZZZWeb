from lrcup import LRCLib
lrclib = LRCLib()

results = lrclib.search(
    track = "Never Gonna Give You Up",
    artist = "Rick Astley"
)
print(results[0]["syncedLyrics"])