""" Master console script for the Spectra program. Contains all entry points. """

import sys
from functools import partial

from spectra_lexer import Component, core, gui_qt, plover, steno, tools
from spectra_lexer.app import Application
from spectra_lexer.batch import BatchProcessor


class EntryPoint:
    """ Wrapper for a console script entry point. Keywords are assigned to the entry point object as attributes.
        Arguments may include component classes, modules, and additional normal and command line arguments.
        If a module has an unwanted component class, adding that class again will *remove* it. """
    def __init__(self, *ep_args, args=(), cmd_args=(), **attrs):
        self.__dict__ = attrs
        self.ep_args = ep_args
        self.args = args
        self.cmd_args = cmd_args

    def __call__(self, *args):
        """ Add command-line arguments, unpack all component classes found in modules, and start the application. """
        sys.argv += self.cmd_args
        classes = [cls for m in self.ep_args for cls in (m, *vars(m).values())
                   if isinstance(cls, type) and issubclass(cls, Component)]
        return Application(*classes).start(*self.args, *args)


class Spectra:
    """ Container class for all entry points to the Spectra program, and the top-level class in the hierarchy. """
    @classmethod
    def get_ep_matches(cls, key:str) -> list:
        """ Get all entry points that match the given key up to its last character. """
        return [ep for attr, ep in vars(cls).items() if attr.startswith(key)]
    # Run the Spectra program by itself in batch mode. Interactive steno components are not required for this.
    analyze = EntryPoint(core, steno.basic, BatchProcessor, args=["lexer_query_all"],
                         desc="run the lexer on every item in a JSON steno translations dictionary.")
    index = EntryPoint(core, steno.basic, BatchProcessor, args=["index_generate"],
                       desc="analyze a translations file and index each translation by the rules it uses.")
    # Run the Spectra program by itself with the standard GUI. The GUI should start first for smoothest operation.
    gui = EntryPoint(core, steno, gui_qt, tools, desc="run the interactive GUI application by itself.")
    # Run the Spectra program as a plugin for Plover. Running it with no args starts a standalone test configuration.
    plugin = EntryPoint(core, steno, gui_qt, tools, plover, cmd_args=["--translations-files=NULL.json"],
                        desc="run the GUI application in Plover plugin mode.",
                        # Class constants required by Plover for toolbar.
                        __doc__='See the breakdown of words using steno rules.',
                        TITLE='Spectra',
                        ICON=':/spectra_lexer/icon.svg',
                        ROLE='spectra_dialog',
                        SHORTCUT='Ctrl+L')


def main():
    """ Main console entry point for the Spectra steno lexer. """
    script, *args = sys.argv
    # The first argument determines the entry point/mode to run.
    # All subsequent arguments are command-line options for that mode.
    # With no arguments, redirect to the standalone GUI app.
    mode, *cmd_opts = args or ["gui"]
    # Make sure the mode matches exactly one entry point function.
    matches = Spectra.get_ep_matches(mode)
    if not matches:
        print(f'No matches for operation "{mode}"')
        return
    if len(matches) > 1:
        print(f'Multiple matches for operation "{mode}". Use more characters.')
        return
    # Reassign the remaining arguments to sys.argv and run the entry point.
    sys.argv = [script, *cmd_opts]
    matches[0]()


if __name__ == '__main__':
    main()
