#!/usr/bin/env python

import os
import sys

import argparse
from jinja2 import Environment, FileSystemLoader, StrictUndefined


def process_templates(options):
    env = Environment(loader=FileSystemLoader(options.template_root),
                keep_trailing_newline=True, undefined=StrictUndefined)

    for root, dirs, files in os.walk(options.template_root):
        for file in files:
            template_file = os.path.relpath(os.path.join(root, file),
                    options.template_root)
            output_file = os.path.join(options.output_root, template_file)

            output_dir = os.path.dirname(output_file)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            template = env.get_template(template_file)
            template.stream(os.environ).dump(output_file)


def exec_command(options):
    args = [options.command] + options.command_args
    if options.command:
        os.execvp(options.command, args)


def parse_args(args=None):
    parser = argparse.ArgumentParser(description='Render a directory hierarchy '
            'of templates using environment variables and optionally execute a '
            'command.')
    parser.add_argument('template_root', metavar='TEMPLATE_ROOT',
            help='directory containing a directory structure with templates')
    parser.add_argument('output_root', metavar='OUTPUT_ROOT',
            help='output directory')
    parser.add_argument('command', metavar='COMMAND [ARGS...]', nargs='?',
            help='an optional command to execute after template processing')
    parser.add_argument('command_args', nargs='*', help=argparse.SUPPRESS)
    parser.epilog = '''
        The template directory file hierarchy will be maintained in the output
        directory. For example, TEMPLATE_ROOT/some/file.txt will be rendered as
        OUTPUT_ROOT/some/file.txt.
    '''
    return parser.parse_args(args)


def main():
    options = parse_args()
    process_templates(options)
    exec_command(options)


if __name__ == '__main__':
    main()
