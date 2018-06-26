"""Output LaTeX for discord nametags.

This command generates LaTeX source for printed nametags for users in
nametagbot's roster.

"""

import argparse
import logging

from .config import Config


def main():
    logging.basicConfig(level=logging.INFO)

    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('-c', '--config', type=str, help='configuration file path')
    p.add_argument(
        '-o',
        '--only-attending',
        action='store_true',
        help='only include users marked as attending')
    p.add_argument('output_dir', type=str, help='output directory path')
    args = p.parse_args()

    config = Config(args.config)
    _write_latex(config, args.only_attending, args.output_dir)


def _write_latex(config, only_attending, output_dir):
    roster = config.get_roster()

    # TODO(mshroyer): Honor only_attending parameter.
    users = roster.attending_users()
