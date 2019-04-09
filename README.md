# lbry-channel-mirror

Tool to synchronize files from a lbry channel to a local directory.

## Install

```
pip install -r requirements.txt
```

## Usage

Create a ```lbry_mirror.yaml``` file (see included example.) Configure the channel you want to mirror.

Examples

```
$ python main.py file_list
Loaded config file: C:\Users\Ryan\Documents\lbry-channel-mirror\lbry_mirror.yaml
File list for channel @EnigmaCurry :
+------------------------------------------|-----------------------------------------|-------------+
|                 claim_id                 |                file_name                | total_bytes |
+==========================================+=========================================+=============+
| e49282c173d55ec33da0f85a3322fcf60b107240 | EnigmaCurry - 2017 - Aeolian Random.mp3 | 5.7 MiB     |
+------------------------------------------|-----------------------------------------|-------------+


$ python main.py file_list --channel @TheLinuxGamer
File list for channel @TheLinuxGamer :
+------------------------------------------|------------------------------------|-------------+
|                 claim_id                 |             file_name              | total_bytes |
+==========================================+====================================+=============+
| 566d88407c474602bae4665d8676e1f981134f25 | major-proton-steam-play-update.mp4 | 70.1 MiB    |
+------------------------------------------|------------------------------------|-------------+
```

## Open Questions

What RPC method to call to get all of the files offered for a channel? file_list only shows the files already downloaded.
