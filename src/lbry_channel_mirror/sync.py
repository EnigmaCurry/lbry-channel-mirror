from lbry_channel_mirror import config as Config
import os
import shutil
import mimetypes
import time
import logging
import re
import unicodedata
import urllib.request

log = logging.getLogger("sync")

def guess_file_name(claim):

    def guess_extension(media_type):
        if media_type == "audio/mpeg":
            return ".mp3"
        else:
            ext = mimetypes.guess_extension(media_type)
            if ext is None:
                return ""
            else:
                return ext

    def normalize_filename(name):
        pattern = re.compile("[\w\-. ]")
        parts = []
        for ch in name:
            if pattern.match(ch):
                parts.append(ch)
            else:
                parts.append("-")
        return "".join(parts)

    name = claim['name']
    media_type = claim['value']['source']['media_type']
    return normalize_filename("{name}{ext}".format(
        name=name, ext=guess_extension(media_type)))

def get_channel_id(client, channel_name):
    channel = next(client.resolve({"urls": [channel_name]}))
    try:
        channel_id = channel[channel_name]['certificate']['claim_id']
    except KeyError:
        raise RuntimeError("Could not find channel_id for {c}".format(
            c=channel_name))
    return channel_id

def fetch(client, config):
    """Gather new claims from the blockchain, and write them to the config file"""
    channel_id = get_channel_id(client, config['channel'])
    remote_claims = []

    if "claims" not in config:
        log.warn("No existing claims found in configuration, starting from scratch.")
        config['claims'] = {}
    else:
        log.info("loaded {x} existing claims".format(x=len(config['claims'])))

    log.info("Searching for claims ... ")
    for remote_claim in client.claim_search({"channel_id": channel_id}):
        remote_claims.extend(remote_claim['items'])

    new_entries = []
    for remote_claim in remote_claims:
        filename = guess_file_name(remote_claim)
        claim_id = remote_claim['claim_id']
        try:
            # Get existing claim entry:
            claim = config['claims'][claim_id]
        except KeyError:
            # This is a new claim entry:
            claim = config['claims'][claim_id] = {'file_name': filename}
            new_entries.append(claim)

    if len(new_entries):
        Config.save(config)
        log.info("Added {x} new claims to config: {p}".format(x=len(new_entries), p=config["config_path"]))
    else:
        log.info("No new claims to fetch.")

def pull(client, config):
    """Download configured files if not existing locally"""
    channel_name = config['channel']
    channel_id = get_channel_id(client, config['channel'])
    remote_claims = {} # name -> claim
    log.info("Searching for {x} claims ... ".format(x=len(config['claims'])))
    for claim_id in config['claims'].keys():
        claim = next(client.claim_search({"claim_id": claim_id}))
        for i in claim['items']:
            remote_claims[claim_id] = i


    ## Gather files to download
    num_active_downloads = config.get('num_active_downloads', 3)
    download_queue = [] # claims to download
    new_downloads = [] # keep track of each file that didn't exist previously so we can delete later
    in_progress = {} # claim_id -> file_list response
    for claim_id, claim in remote_claims.items():
        download_exists = len(next(client.file_list({"claim_id": claim_id}))) > 0
        filename = config['claims'][claim_id]['file_name']
        # Check if file does not already exist in the final output directory:
        if not os.path.exists(os.path.join(config['download_directory'], filename)):
            # Only log about the ones that really need to be downloaded:
            if not download_exists:
                log.debug("Queued Download: {u} : {f}".format(u=claim['name'], f=filename))
            # Queue files for download:
            download_queue.append(claim)
            new_downloads.append(claim_id)

    num_complete = 0

    # Wait for downloads to finish, then copy to the final directory:
    while len(in_progress) or len(download_queue):
        # Start new downloads from the queue:
        for x in range(len(in_progress), num_active_downloads):
            try:
                claim = download_queue.pop(0)
            except IndexError:
                # No more downloads
                break
            claim_id = claim['claim_id']
            uri = "{channel}/{name}".format(channel=channel_name, name=claim['name'])
            filename = config['claims'][claim_id]['file_name']
            in_progress[claim_id] = next(client.get({"uri": uri, "save_file": False}))
            log.info("Started Download: {u} : {f}".format(u=claim['name'], f=filename))

        # Process the in progress downloads:
        for claim_id, dl in list(in_progress.items()):
            filename = config['claims'][claim_id]['file_name']
            if dl['blobs_remaining'] == 0:
                # Download Complete.
                # Stream the file to the final location:
                log.info("Saving file: {f}".format(f=filename))
                stream_url = "{endpoint}/get/{name}/{claim_id}".format(
                    claim_id=claim_id, name=claim['name'],
                    endpoint=config['endpoint']
                )
                print(stream_url)
                dest_path = os.path.join(config['download_directory'], filename)
                with urllib.request.urlopen(stream_url) as response, \
                     open(dest_path, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)

                del in_progress[claim_id]
                log.info("Download Complete: {f}".format(f=filename))
                num_complete += 1
            else:
                in_progress[claim_id] = next(client.file_list({"claim_id": claim_id}))[0]
                log.info("Download Progress: {f} - blobs remaining: {blobs}".format(
                    f=filename, blobs=dl['blobs_remaining']))
        time.sleep(10)

    log.info("{x} files downloaded.".format(x=num_complete))
