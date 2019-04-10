from lbry_client import LbryRpcClient
import config
import sys
import shutil
import argparse
import humanize
from texttable import Texttable as TextTable
import logging
import pprint

class CommandLine:
    # Thank you Chase Seibert for the pattern -
    # https://dzone.com/articles/multi-level-argparse-python
    def __init__(self):
        self.main = argparse.ArgumentParser(usage = """%(prog)s <command> [options]

Examples (append --help to any command for more info):
  Show current sync status:          %(prog)s status
  Search for all channel claims:     %(prog)s claim_search

Utility functions:
  Resolve lbry URLs:                 %(prog)s resolve @EnigmaCurry @giuseppe
  Search for claims by id:           %(prog)s claim_search 9e2f40110d9f121b1caa0661133bac353ef66a71
        """)
        self.main.add_argument('command', help="Subcommand to run")
        args = self.main.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            self.main.print_help()
            print("\nUnrecognized command: {}".format(args.command))
            exit(1)
        self.__pprint = pprint.PrettyPrinter(indent=2)
        getattr(self, args.command)()

    def __print_table(self, header, rows):
        table = TextTable(max_width=shutil.get_terminal_size((80, 20)).columns)
        table.header(header)
        for r in rows:
            table.add_row(r)
        print(table.draw())

    def __create_subcommand(self, name, arguments=[], skip_default_args=[], description=""):
        parser = argparse.ArgumentParser(usage="%(prog)s {name} [options]\n\n{desc}".format(
            name=name, desc=description))
        if 'endpoint' not in skip_default_args:
            parser.add_argument('--endpoint', default="http://localhost:5279/",
                                help="The LBRY RPC endpoint URL")
        if 'channel' not in skip_default_args:
            parser.add_argument('--channel', default=None, help="Override the channel in the config file")
        if 'config' not in skip_default_args:
            parser.add_argument('--config', default="lbry_mirror.yaml",
                                help="The path to the config yaml file for %(prog)s")
        if 'verbose' not in skip_default_args:
            parser.add_argument('--verbose', action="store_true")
        for arg in arguments:
            name, params = (arg['name'], arg.get('params', {}))
            parser.add_argument(name, **params)
        args = parser.parse_args(sys.argv[2:])

        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        self.__client = LbryRpcClient(args.endpoint)
        self.__config = config.load()
        if hasattr(args, 'channel') and args.channel is not None:
            self.__config = {"channel": args.channel}
        return args

    def status(self):
        args = self.__create_subcommand("status")
        print("unimplemented, sorry")
        exit(1)

    def resolve(self):
        """Resolve lbry URLs or the channel itself if no urls are specified"""
        args = self.__create_subcommand("resolve", [{"name": "urls", "params":{"nargs": "*"}}])
        channel_name = self.__config['channel']
        if len(args.urls) == 0:
            # Resolve configured channel:
            urls = [channel_name]
        else:
            # Resolve provided URLs:
            urls = args.urls
        self.__pprint.pprint(self.__client.resolve({"urls": urls}))

    def file_list(self):
        """Show all downloaded files"""
        args = self.__create_subcommand("file_list",
                                        description=self.file_list.__doc__)
        channel = self.__config['channel']
        files = self.__client.file_list({"channel_name": self.__config['channel']})

        print("Downloaded files for channel {} :".format(channel))
        self.__print_table(header=["claim_id", "file_name", "total_bytes"],
                           rows=[[
                               f["claim_id"],
                               f["file_name"],
                               humanize.naturalsize(f["total_bytes"], binary=True)
                           ] for f in files])

    def claim_search(self):
        """Search for all the channel claims, or from a given list of claim ids"""
        args = self.__create_subcommand(
            "claim_search", [{"name": "claim_ids", "params": {"nargs":"*"}}],
            description=self.claim_search.__doc__)
        channel_name = self.__config['channel']

        if len(args.claim_ids):
            # Search for claim ids:
            for claim_id in args.claim_ids:
                print("")
                self.__pprint.pprint(self.__client.claim_search({"claim_id": claim_id}))
        else:
            # Search for all claims in the channel:
            channel = self.__client.resolve({"urls": [channel_name]})

            try:
                channel_id = channel[channel_name]['certificate']['claim_id']
            except KeyError:
                logging.error("Error in resolve response: {c}".format(c=channel))
                raise RuntimeError("Could not find channel_id for {c}".format(
                    c=channel_name))

            claims = self.__client.claim_search({"channel_id": channel_id})
            assert 'items' in claims, "Invalid claims response: {c}".format(c=claims)

            print("Streams for channel {c} :".format(c=channel_name))
            print("Channel id: {id}".format(id=channel_id))
            self.__print_table(header=["permanent_url", "claim_id"],
                               rows= [[
                                   f["permanent_url"],
                                   f["claim_id"],
                               ] for f in claims['items']])

if __name__ == "__main__":
    CommandLine()
