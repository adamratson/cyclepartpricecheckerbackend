import partdler
import os
import json

crc = partdler.CRC()
f = open(os.path.join("..", "json", "wpd.json"), "w")
json.dump(wpd.main(), f)
f.close()
