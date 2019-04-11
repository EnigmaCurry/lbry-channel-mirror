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

Create a `lbry_channel__mirror.yaml` file inside a directory anywhere you like. (See included example.) Configure the channel you want to mirror.

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
`lbry_channel_mirror.yaml` file as `mirror_ids`. But you don't have to create
this list by hand, the `fetch` command will do that for you.

Create a config file with just the channel name you wish to mirror. Create `lbry_channel_mirror.yaml`:

```
channel: '@EnigmaCurry'
```

Run `lbry_channel_mirror fetch`. This will search for all of the claims made for the channel `@EnigmaCurry` and save them to the config:

After running `fetch`, your `lbry_channel_mirror.yaml` file now contains all the
latest claims for the channel you're mirroring:

```
channel: '@EnigmaCurry'
mirror_ids:
- e49282c173d55ec33da0f85a3322fcf60b107240
- 045fd2680317e998e87944e4fb875ceb4d3b8f3c
- 9fb0396bc923f8f68c549cac6907295933bd37df
- 07106ed49e2264e6a766c80996d1e8b719cd5b60
- 824e84c720c9968493aaf568f053f230c7e282cb
```

Now run `lbry_channel_mirror pull` to download the files to the same directory as `lbry_channel_mirror.yaml`

Remember, all streams must be listed in the config file first, before they can be
pulled. You can edit the config file by hand, or add new claim_ids by running
`fetch` again. 
