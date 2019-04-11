# lbry-channel-mirror

Tool to synchronize files from a lbry channel to a local directory.

## Build exe

```
git clone https://github.com/EnigmaCurry/lbry-channel-mirror.git
cd lbry-channel-mirror
pip install -r requirements.txt
python setup.py build_exe
```

After it builds, find the all-in-one executable file in the ```dist```
directory.

## Usage

Create a ```lbry_channel__mirror.yaml``` file inside a directory anywhere you like. (See included example.) Configure the channel you want to mirror.

See command examples by running the builtin help:

```
lbry_channel_mirror --help
```

or see the help for any subcommand:

```
lbry_channel_mirror resolve --help
```
