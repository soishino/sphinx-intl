# -*- coding: utf-8 -*-
"""
    sphinx-intl
    ~~~~~~~~~~~
    Sphinx utility that make it easy to translate and to apply translation.

    :copyright: Copyright 2019 by Takayuki SHIMIZUKAWA.
    :license: BSD, see LICENSE for details.
"""
import re
import os
from glob import glob

import click
from sphinx.util.tags import Tags

from . import basic
from . import transifex
from .pycompat import execfile_, relpath

ENVVAR_PREFIX = 'SPHINXINTL'


# ==================================
# utility functions

def read_config(path, passed_tags):

    tags = Tags()
    passed_tags = sum(passed_tags, ())
    for tag in passed_tags:
        tags.add(tag)

    namespace = {
        "__file__": os.path.abspath(path),
        "tags": tags,
    }

    olddir = os.getcwd()
    try:
        if not os.path.isfile(path):
            msg = "'%s' is not found (or specify --locale-dir option)." % path
            raise click.BadParameter(msg)
        os.chdir(os.path.dirname(path) or ".")
        execfile_(os.path.basename(path), namespace)
    finally:
        os.chdir(olddir)

    return namespace


def get_lang_dirs(path):
    dirs = [relpath(d, path)
            for d in glob(path+'/[a-z]*')
            if os.path.isdir(d) and not d.endswith('pot')]
    return (tuple(dirs),)


# ==================================
# click options

class LanguagesType(click.ParamType):
    name = 'languages'
    envvar_list_splitter = ','

    def convert(self, value, param, ctx):
        langs = value.split(',')
        return tuple(langs)


LANGUAGES = LanguagesType()


class TagsType(click.ParamType):
    name = 'tags'
    envvar_list_splitter = ','

    def convert(self, value, param, ctx):
        tags = value.split(',')
        return tuple(tags)


TAGS = TagsType()


option_locale_dir = click.option(
    '-d', '--locale-dir',
    envvar=ENVVAR_PREFIX + '_LOCALE_DIR',
    type=click.Path(exists=False, file_okay=False),
    default='locales', metavar='<DIR>', show_default=True,
    help='locale directories that allow comma separated string. This option '
         'override locale_dir in conf.py setting if provided. Default is empty '
         'list.')

option_pot_dir = click.option(
    '--pot-dir', '-p',
    envvar=ENVVAR_PREFIX + '_POT_DIR',
    type=click.Path(exists=False, file_okay=False),
    metavar='<DIR>', show_default=True,
    help="pot files directory which is generated by sphinx. "
         "Default is 'pot' directory under '--locale-dir' path.")

option_output_dir = click.option(
    '--output-dir', '-o',
    envvar=ENVVAR_PREFIX + '_OUTPUT_DIR',
    type=click.Path(exists=False, file_okay=False),
    metavar='<DIR>', show_default=True,
    help="mo files directory where files are written. "
         "Default is to match the '--locale-dir' path.")

option_tag = click.option(
    '-t', '--tag',
    envvar=ENVVAR_PREFIX + '_TAG',
    type=TAGS, default=(), metavar='<TAG>', show_default=True,
    multiple=True,
    help="Pass tags to conf.py, as same as passed to sphinx-build -t option.")

option_language = click.option(
    '-l', '--language',
    envvar=ENVVAR_PREFIX + '_LANGUAGE',
    type=LANGUAGES, default=(), metavar='<LANG>', show_default=True,
    multiple=True,
    help="Target language to update po files. Default is ALL.")

option_line_width = click.option(
    '-w', '--line-width',
    envvar=ENVVAR_PREFIX + '_LINE_WIDTH',
    type=int, default=76, metavar='<WIDTH>', show_default=True,
    multiple=False,
    help='The maximum line width for the po files, 0 or a negative number '
         'disable line wrapping')

option_transifex_username = click.option(
    '--transifex-username',
    envvar=ENVVAR_PREFIX + '_TRANSIFEX_USERNAME',
    type=str, metavar='<USERNAME>', show_default=True,
    help="Your transifex username. Default is None.")

option_transifex_password = click.option(
    '--transifex-password',
    envvar=ENVVAR_PREFIX + '_TRANSIFEX_PASSWORD',
    type=str, metavar='<PASSWORD>', show_default=True,
    help="Your transifex password. Default is None.")

option_transifex_project_name = click.option(
    '--transifex-project-name',
    envvar=ENVVAR_PREFIX + '_TRANSIFEX_PROJECT_NAME',
    type=str, metavar='<PROJECT-NAME>', show_default=True,
    help="Your transifex project name. default is None")


# ==================================
# commands

@click.group()
@click.option(
    '-c', '--config',
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    default=None, metavar='<FILE>',
    help='Sphinx conf.py file to read a locale directory setting.')
@option_tag
@click.pass_context
def main(ctx, config, tag):
    """
    Environment Variables:
    All command-line options can be set with environment variables using the
    format SPHINXINTL_<UPPER_LONG_NAME> . Dashes (-) have to replaced with
        underscores (_).

    For example, to set the languages:

    export SPHINXINTL_LANGUAGE=de,ja

    This is the same as passing the option to txutil directly:

    sphinx-intl update --language=de --language=ja
    """
    # load conf.py
    ctx.config = config
    if ctx.config is None:
        for c in ('conf.py', 'source/conf.py'):
            if os.path.exists(c):
                ctx.config = c
                break

    # for locale_dir
    ctx.locale_dir = None
    if ctx.config:
        cfg = read_config(ctx.config, tag)
        if 'locale_dirs' in cfg:
            ctx.locale_dir = os.path.join(
                os.path.dirname(ctx.config), cfg['locale_dirs'][0])

    # for pot_dir
    ctx.pot_dir = None
    for d in ('_build/gettext', 'build/gettext',
              '_build/locale', 'build/locale'):
        if os.path.exists(d):
            ctx.pot_dir = d
            break

    # for transifex_project_name
    ctx.transifex_project_name = None
    target = os.path.normpath('.tx/config')
    if os.path.exists(target):
        matched = re.search(r'\[(.*)\..*\]', open(target, 'r').read())
        if matched:
            ctx.transifex_project_name = matched.groups()[0]
            click.echo(
                'Project name loaded from .tx/config: {0}'.format(
                    ctx.transifex_project_name))

    ctx.default_map = {
        'update': {
            'locale_dir': ctx.locale_dir,
            'pot_dir': ctx.pot_dir,
        },
        'build': {
            'locale_dir': ctx.locale_dir,
        },
        'stat': {
            'locale_dir': ctx.locale_dir,
        },
        'update-txconfig-resources': {
            'locale_dir': ctx.locale_dir,
            'pot_dir': ctx.pot_dir,
            'transifex_project_name': ctx.transifex_project_name,
        },
    }


@main.command()
@option_locale_dir
@option_pot_dir
@option_language
@option_line_width
def update(locale_dir, pot_dir, language, line_width):
    """
    Update specified language's po files from pot.

    \b
    For examples:
       sphinx-intl update -l de -l ja
       sphinx-intl update -l de,ja
    """
    if not pot_dir:
        pot_dir = os.path.join(locale_dir, 'pot')
    if not os.path.exists(pot_dir):
        msg = ("%(pot_dir)r does not exist. Please specify pot directory with "
               "-p option, or preparing your pot files in %(pot_dir)r."
               % locals())
        raise click.BadParameter(msg, param_hint='pot_dir')
    if not language:
        language = get_lang_dirs(locale_dir)
    languages = sum(language, ())  # flatten
    if not languages:
        msg = ("No languages are found. Please specify language with -l "
               "option, or preparing language directories under %(locale_dir)r "
               "directory."
               % locals())
        raise click.BadParameter(msg, param_hint='language')

    basic.update(locale_dir, pot_dir, languages, line_width)


@main.command()
@option_locale_dir
@option_output_dir
@option_language
def build(locale_dir, output_dir, language):
    """
    Build specified language's po files into mo.
    """
    if not language:
        language = get_lang_dirs(locale_dir)
    languages = sum(language, ())  # flatten

    if not output_dir or (
            os.path.exists(output_dir) and
            os.path.samefile(locale_dir, output_dir)):
        output_dir = locale_dir

    basic.build(locale_dir, output_dir, languages)


@main.command()
@option_locale_dir
@option_language
def stat(locale_dir, language):
    """
    Print statistics for all po files.
    """
    if not language:
        language = get_lang_dirs(locale_dir)
    languages = sum(language, ())  # flatten
    basic.stat(locale_dir, languages)


@main.command('create-transifexrc')
@option_transifex_username
@option_transifex_password
def create_transifexrc(transifex_username, transifex_password):
    """
    Create `$HOME/.transifexrc`
    """
    transifex.create_transifexrc(transifex_username, transifex_password)


@main.command('create-txconfig')
def create_txconfig():
    """
    Create `./.tx/config`
    """
    transifex.create_txconfig()


@main.command('update-txconfig-resources')
@option_transifex_project_name
@option_locale_dir
@option_pot_dir
def update_txconfig_resources(transifex_project_name, locale_dir, pot_dir):
    """
    Update resource sections of `./.tx/config`.
    """
    if not pot_dir:
        pot_dir = os.path.join(locale_dir, 'pot')

    transifex.update_txconfig_resources(transifex_project_name, locale_dir, pot_dir)


if __name__ == '__main__':
    main(auto_envvar_prefix=ENVVAR_PREFIX)
