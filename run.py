#!/usr/bin/env python
"""
usage: run.py [-h]

The entry point for the DJ Music App Suite.

positional arguments:
  {dml,}
    downloadMusicList            Download files from xlsx file
    audioMigration               Migrate files from one folder to another

optional arguments:
  -h, --help            show this help message and exit

"""
import argparse
from src.config import get_config
from src.config import get_logger, get_enabled_commands

logger = get_logger(__name__)

# Access argpars Namespace using get method
setattr(argparse.Namespace, "get", lambda self, key: self.__dict__.get(key))


def no_sub_command(args):
    print("No sub command specified, use --help for more info.")
    command_cannot_be_executed = 126
    exit(command_cannot_be_executed)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="The entry point the MapRisk Data Utility."
    )

    DEFAULT_ENV = get_config("general", "default_env", "dev")

    parser.set_defaults(func=no_sub_command)
    # parser.add_argument(
    #     "--env",
    #     default=DEFAULT_ENV,
    #     type=str,
    #     choices=get_envs(),
    #     # required=True,
    #     help=f"Environment, specify the environment before the subcommand default ({DEFAULT_ENV})",
    # )

    subparsers = parser.add_subparsers()
    for sub_parser in get_enabled_commands():
        logger.debug(f"Loading {sub_parser} command")
        sp_mod = __import__(f"src.subparsers.{sub_parser}", fromlist=[""])
        sp_mod.create_subparser(subparsers)

    args = parser.parse_args()
    args.func(args)
