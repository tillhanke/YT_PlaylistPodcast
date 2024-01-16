Download all mp3s as well as meta info of the playlist via:

```yt-dlp --yes-playlist -x --audio-format=mp3 --write-info-json ```

Then all data should be processed via:
```bash
IFS=$'\n'
for json in $(/bin/ls *.json| grep "[0-9]\{3\}");do ./json_to_item.py $json;done
```
the regex is specific to the numbering of the podcast episodes
