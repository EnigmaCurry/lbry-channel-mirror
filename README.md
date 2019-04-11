# lbry-channel-mirror

Tool to synchronize files from a lbry channel to a local directory.

## Build exe

```
git clone https://github.com/EnigmaCurry/lbry-channel-mirror.git
cd lbry-channel-mirror
pip install -r requirements.txt
python setup.py build_exe
```

After it builds, find the all-in-one executable file in the `dist`
directory.

## Usage

See command examples by running the builtin help:

```
lbry_channel_mirror --help
```

or see the help for any subcommand:

```
lbry_channel_mirror resolve --help
```

### Downloading all channel content

`lbry_channel_mirror` will only download the claims that are listed in your
`lbry_channel_mirror.yaml` file as `claims`. But you don't have to create
this list by hand, the `fetch` command will do that for you.

In a blank directory, or in a directory of files you wish to publish, initialize
lbry_channel_mirror with the name of the channel you wish to mirror:

```
lbry_channel_mirror init --channel @EnigmaCurry
```

This creates a config file (`lbry_channel_mirror.yaml`) with the following:

```
channel: '@EnigmaCurry'
```

The tool can search for all the claims for this channel and automatically fill your config file:

```
lbry_channel_mirror fetch
```

After running `fetch`, your `lbry_channel_mirror.yaml` file now contains all the
latest claims for the channel you're mirroring:

```
channel: '@EnigmaCurry'
claims:
  045fd2680317e998e87944e4fb875ceb4d3b8f3c:
    file_name: No Minor Sea.mp4
  07106ed49e2264e6a766c80996d1e8b719cd5b60:
    file_name: Docetic Bodhisattva (his noetic body sought ya).mp4
  824e84c720c9968493aaf568f053f230c7e282cb:
    file_name: Waiting for Nothing - The Iridule.mp4
  9fb0396bc923f8f68c549cac6907295933bd37df:
    file_name: Akashic Diffusion - Carbon Collector at Emerald Station.mp4
  e49282c173d55ec33da0f85a3322fcf60b107240:
    file_name: EnigmaCurry - 2017 - Aeolian Random (2).mp3
```

Now run `lbry_channel_mirror pull` to download the files to the same directory
(or whatever directory that contains the config passed with `--config`).

Remember, all streams must be listed in the config file first, before they can
be pulled. You can edit the config file by hand, or search for new claim_ids and
add them automatically, by running `fetch` again.
