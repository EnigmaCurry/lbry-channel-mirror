from lbry_client import LbryRpcClient
import config
import sys
import shutil
import argparse
import humanize
from texttable import Texttable as TextTable
import logging

class CommandLine:
    # Thank you Chase Seibert for the pattern -
    # https://dzone.com/articles/multi-level-argparse-python
    def __init__(self):
        self.main = argparse.ArgumentParser(usage = """%(prog)s <command> [options]

Examples:
        %(prog)s file_list
        """)
        self.main.add_argument('command', help="Subcommand to run")
        args = self.main.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            self.main.print_help()
            print("\nUnrecognized command: {}".format(args.command))
            exit(1)
        getattr(self, args.command)()

    def __print_table(self, header, rows):
        table = TextTable(max_width=shutil.get_terminal_size((80, 20)).columns)
        table.header(header)
        for r in rows:
            table.add_row(r)
        print(table.draw())

    def __create_subcommand(self, name, arguments=[]):
        parser = argparse.ArgumentParser(usage="%(prog)s {name} [options]".format(name=name))
        parser.add_argument('--endpoint', default="http://localhost:5279/", help="The LBRY RPC endpoint URL")
        parser.add_argument('--channel', default=None, help="Override the channel in the config file")
        parser.add_argument('--config', default="lbry_mirror.yaml", help="The path to the config yaml file for %(prog)s")
        parser.add_argument('--verbose', action="store_true")
        for arg in arguments:
            parser.add_argument(arg.name, **arg.params)
        args = parser.parse_args(sys.argv[2:])

        if args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        self.__client = LbryRpcClient(args.endpoint)
        if args.channel:
            self.__config = {"channel": args.channel}
        else:
            self.__config = config.load()
        return

    def file_list(self):
        args = self.__create_subcommand("file_list")
        channel = self.__config['channel']
        files = self.__client.file_list({"channel_name": self.__config['channel']})

        print("File list for channel {} :".format(channel))
        header = ["claim_id", "file_name", "total_bytes"]
        rows = [[
            f["claim_id"],
            f["file_name"],
            humanize.naturalsize(f["total_bytes"], binary=True)
        ] for f in files]
        self.__print_table(header, rows)

    def claim_search(self):
        args = self.__create_subcommand("claim_search")
        channel = self.__config['channel']
        claims = self.__client.claim_search({"channel_id": self.__config['channel']})

        print("Claim list for channel {} :".format(channel))
        print(claims)
        # header = ["claim_id", "file_name", "total_bytes"]
        # rows = [[
        #     f["claim_id"],
        #     f["file_name"],
        #     humanize.naturalsize(f["total_bytes"], binary=True)
        # ] for f in files]
        # self.__print_table(header, rows)


if __name__ == "__main__":
    CommandLine()
