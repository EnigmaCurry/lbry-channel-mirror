from lbry_channel_mirror import config as Config
import os
import shutil
import mimetypes
import time
import logging

def guess_file_name(stream):
    def guess_extension(media_type):
        if media_type == "audio/mpeg":
            return ".mp3"
        else:
            return mimetypes.guess_extension(media_type)
    title = stream['title']
    media_type = stream['media_type']
    return "{name}{ext}".format(
        name=title, ext=guess_extension(media_type))

def get_channel_id(client, config):
    channel_name = config['channel']
    channel = next(client.resolve({"urls": [channel_name]}))
    try:
        channel_id = channel[channel_name]['certificate']['claim_id']
    except KeyError:
        raise RuntimeError("Could not find channel_id for {c}".format(
            c=channel_name))
    return channel_id

def fetch(client, config):
    """Gather new claims from the blockchain, and write them to the config file"""
    channel_id = get_channel_id(client, config)
    remote_claims = []
    for remote_claim in client.claim_search({"channel_id": channel_id}):
        remote_claims.extend(remote_claim['items'])

    if not hasattr(config, "claims"):
        config['claims'] = {}

    new_entries = []
    for remote_claim in remote_claims:
        filename = guess_file_name(remote_claim['value']['stream'])
        claim_id = remote_claim['claim_id']
        try:
            # Get existing claim entry:
            claim = config['claims'][claim_id]
        except KeyError:
            # This is a new claim entry:
            claim = config['claims'][remote_claim['claim_id']] = {'file_name': filename}
            new_entries.append(claim)

    if len(new_entries):
        Config.save(config)
        logging.info("Added {x} new claims to config: {p}".format(x=len(new_entries), p=config["config_path"]))

def pull(client, config):
    """Download configured files if not existing locally"""
    channel_name = config['channel']
    channel_id = get_channel_id(client, config)
    remote_claims = {} # name -> claim
    for claim_id in config['claims'].keys():
        claim = next(client.claim_search({"claim_id": claim_id}))
        for i in claim['items']:
            remote_claims[claim_id] = i

    new_downloads = [] # keep track of each file that didn't exist previously so we can delete later
    downloads = {} # claim_id -> file_list response
    for claim_id, claim in remote_claims.items():
        download_exists = len(next(client.file_list({"claim_id": claim_id}))) > 0
        filename = config['claims'][claim_id]['file_name']
        if not os.path.exists(os.path.join(config['download_directory'], filename)):
            # Download the file
            if not download_exists:
                logging.info("Starting Download: {f}".format(f=filename))
            downloads[claim['claim_id']] = next(client.get({"uri": claim['name']}))
            new_downloads.append(claim_id)

    num_complete = 0

    # Wait for downloads to finish, then copy to the final directory:
    while len(downloads):
        for claim_id, dl in list(downloads.items()):
            filename = config['claims'][claim_id]['file_name']
            if dl['blobs_remaining'] == 0:
                # Complete:
                # Copy to file destination:
                dest_path = os.path.join(
                    config['download_directory'], filename)
                shutil.copy(dl['download_path'], dest_path)
                # Delete temporary download:
                if claim_id in new_downloads:
                    if next(client.file_delete({'claim_id': claim_id})):
                        logging.debug("Deleted temporary download: {f}".format(f=dl['download_path']))
                    else:
                        logging.warn("Failed to delete temporary downloaded file: {f}".format(
                            dl['download_path']))

                del downloads[claim_id]
                logging.info("Download Complete: {f}".format(f=filename))
                num_complete += 1
            else:
                downloads[claim_id] = next(client.file_list({"claim_id": claim_id}))[0]
                logging.info("Download Progress: {f} - blobs remaining: {blobs}".format(
                    f=filename, blobs=dl['blobs_remaining']))
                if dl['blobs_remaining'] > 0:
                    time.sleep(10)
    logging.info("{x} files downloaded.".format(x=num_complete))
