#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
from collections import Hashable
import json
import os
import subprocess
import sys
import traceback

from jinja2 import BaseLoader, Environment, FileSystemLoader, StrictUndefined, \
        Template, UndefinedError
import yaml
from yaml.scanner import ScannerError


class SourceLoader(BaseLoader):
    def get_source(self, environment, template):
        return template, None, lambda: True


def process_templates(vars, options):
    env = get_env(FileSystemLoader(options.template_root))
    for root, dirs, files in os.walk(options.template_root):
        for file in files:
            template_file = os.path.relpath(os.path.join(root, file),
                    options.template_root)
            output_file = os.path.join(options.output_root, template_file)

            output_dir = os.path.dirname(output_file)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            template = env.get_template(template_file)
            output = template.render(vars)
            with open(output_file, 'w') as out:
                out.write(output)


def run_scripts(vars, options):
    try:
        filenames = sorted(os.listdir(options.scripts_root))
    except OSError:
        return
    for filename in filenames:
        script = os.path.join(options.scripts_root, filename)
        try:
            subprocess.call([script])
        except OSError:
            pass


def exec_command(vars, options):
    env = get_env(SourceLoader())
    template = env.get_template(options.command)
    args = [options.command] + options.command_args
    args = [env.get_template(arg).render(vars) for arg in args]
    if options.command:
        os.execvp(args[0], args)


def collect_vars(options):
    if os.path.exists(options.variables_file):
        with open(options.variables_file) as stream:
            vars = yaml.safe_load(stream) or {}
    else:
        vars = {}
    vars.update(os.environ)
    return vars


def get_env(loader):
    env = Environment(loader=loader, keep_trailing_newline=True,
            undefined=StrictUndefined)
    for name, func in filters().items():
        env.filters[name] = func
    return env


# Template filters

def filters():

    def split(value, sep=None, maxsplit=-1):
        return value.split(sep, maxsplit)

    def to_json(value, *args, **kwargs):
        return json.dumps(value, *args, **kwargs)

    def to_nice_json(value, *args, **kwargs):
        return json.dumps(value, indent=4, sort_keys=True, *args, **kwargs)

    def unique(value):
        if isinstance(value, Hashable):
            result = set(value)
        else:
            result = []
            for x in value:
                if x not in result:
                    result.append(x)
        return result

    def intersect(value, other):
        if isinstance(value, Hashable) and isinstance(other, Hashable):
            result = set(value) & set(other)
        else:
            result = unique(filter(lambda x: x in other, value))
        return result

    def difference(value, other):
        if isinstance(value, Hashable) and isinstance(other, Hashable):
            result = set(value) - set(other)
        else:
            result = unique(filter(lambda x: x not in other, value))
        return result

    def symmetric_difference(value, other):
        if isinstance(value,Hashable) and isinstance(other,Hashable):
            result = set(value) ^ set(other)
        else:
            result = unique(filter(lambda x: x not in intersect(value, other),
                    union(value, other)))
        return result

    def union(value, other):
        if isinstance(value, Hashable) and isinstance(other, Hashable):
            result = set(value) | set(other)
        else:
            result = unique(value + other)
        return result

    return locals()


# Command line handling


def parse_args(args=None):
    parser = argparse.ArgumentParser(
            usage='%(prog)s [OPTIONS] [--] COMMAND [ARGS...]',
            description='Render a directory hierarchy '
                'of templates and execute a command.',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-v', '--variables', metavar='VARIABLES',
            dest='variables_file', default='/variables.yml',
            help='optional YAML file containing template variables')
    parser.add_argument('-t', '--templates', metavar='TEMPLATES',
            dest='template_root', default='/templates',
            help='directory structure containing template files')
    parser.add_argument('-o', '--output', metavar='OUTPUT',
            dest='output_root', default='/',
            help='output directory')
    parser.add_argument('-s', '--scripts', metavar='SCRIPTS',
            dest='scripts_root', default='/scripts',
            help='directory containing scripts to run before the command')
    parser.add_argument('command', metavar='COMMAND [ARGS...]',
            help='the command to execute after template processing')
    parser.add_argument('command_args', nargs='*', help=argparse.SUPPRESS)
    parser.epilog = '''
        First, variables are be read from the YAML file VARIABLES and from the
        environment, the latter overriding the former.

        Second, all templates in the TEMPLATES directory are rendered into the
        OUTPUT directory, maintaining the file hierarchy.(For example,
        TEMPLATES/some/file.txt will be rendered as OUTPUT/some/file.txt.)

        Then, any executable script in the SCRIPTS directory are run.

        Finally, the COMMAND is executed. Template variables can also be used in
        the command and its arguments. Add '--' before the command if any ARGS
        start with '-'.
    '''
    return parser.parse_args(args)


def print_exception():
    """Print nicer template and YAML parse errors."""
    exc_type, exc_value, exc_tb = sys.exc_info()
    tb = exc_tb
    while tb is not None:
        if tb.tb_frame.f_code.co_name == 'top-level template code':
            error = traceback.format_exception(exc_type, exc_value, tb)
            error[0] = 'Error rendering templates:\n'
            for line in error:
                sys.stderr.write(line)
            break
        tb = tb.tb_next
    else:
        if exc_type == ScannerError:
            sys.stderr.write('Error ')
            sys.stderr.write(unicode(exc_value))
            sys.stderr.write('\n')
        else:
            traceback.print_exception(exc_type, exc_value, exc_tb)


def main():
    try:
        options = parse_args()
        vars = collect_vars(options)
        process_templates(vars, options)
        run_scripts(vars, options)
        exec_command(vars,  options)
    except Exception:
        print_exception()
        sys.exit(1)



if __name__ == '__main__':
    main()
