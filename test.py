## used for internal testing
import json
# read whosampled.json
with open('sources/whosampled.json', 'r') as f:
    data = json.load(f)

tracks = data['artist_data']['Nujabes']

sum_samples = sum(track['samples'] for track in tracks)
print(sum_samples)
