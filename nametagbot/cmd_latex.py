# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Output LaTeX for discord nametags.

This command generates LaTeX source for printed nametags for users in
nametagbot's roster.

"""

import argparse
import itertools
import jinja2
import logging
import os

from .config import Config

BOX_X_COORDINATES = [0.69, 4.44]
BOX_Y_COORDINATES = [0.56, 3.08, 5.6, 8.13]


def main():
    logging.basicConfig(level=logging.INFO)

    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('-c', '--config', type=str, help='configuration file path')
    p.add_argument(
        '-a',
        '--all',
        action='store_true',
        help='include all users, not only the ones marked attending')
    p.add_argument('output_dir', type=str, help='output directory path')
    args = p.parse_args()

    config = Config(args.config)
    _write_latex(config, args.output_dir)


# http://eosrei.net/articles/2015/11/latex-templates-python-and-jinja2-generate-pdfs
_latex_jinja_env = jinja2.Environment(
    block_start_string='\BLOCK{',
    block_end_string='}',
    variable_start_string='\VAR{',
    variable_end_string='}',
    comment_start_string='\#{',
    comment_end_string='}',
    line_statement_prefix='%%',
    line_comment_prefix='%#',
    trim_blocks=True,
    autoescape=False,
    loader=jinja2.PackageLoader('nametagbot', 'templates'))

_box_coordinates = itertools.cycle(
    map(lambda c: tuple(reversed(c)),
        itertools.product(BOX_Y_COORDINATES, BOX_X_COORDINATES)))


def _write_latex(config, output_dir):
    roster = config.get_roster()
    avatar_cache = config.get_avatar_cache()

    # TODO(mshroyer): Honor 'all' parameter.
    users = list(roster.attending_users()) * 10

    os.mkdir(output_dir)
    os.mkdir(os.path.join(output_dir, 'avatars'))
    for user in users:
        avatar_cache.get_avatar(
            user,
            os.path.join(output_dir, 'avatars',
                         '{user_id}.png'.format(**user._asdict())))

    template = _latex_jinja_env.get_template('nametags.tex')
    template.stream(
        users=zip(users, _box_coordinates), escape=_latex_escape).dump(
            os.path.join(output_dir, 'nametags.tex'))


def _latex_escape(s):
    escapes = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '\\': r'\textbackslash{}',
        '<': r'\textless{}',
        '>': r'\textgreater{}',
    }
    output = []
    for ch in s:
        if ch in escapes:
            output.append(escapes[ch])
        else:
            output.append(ch)

    return ''.join(output)
