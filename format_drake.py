import json

filepath = "Lyrics_ForAllTheDogsScaryHoursEdition.json"

with open(filepath, "r") as file:
  data = json.load(file)
  for track in data['tracks']:
    track['song']

# Q2
# 1. geometric annotated, s looks like 1/t where t is a large number
# 2. follows from the number we get from 1

# Q3
# 1. for number 3 use x_img = Hx_w
# 2. for 4, use x_img = Px_w, we know X,Z from 3 and (x,y) = x_head_img