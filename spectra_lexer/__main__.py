import sys

from spectra_lexer.gui_qt import SpectraGUIQtApplication


def main() -> None:
    """ Main console entry point for the Spectra steno lexer. Should be simple as possible. """
    # For now, the GUI app is always started, and all command-line arguments are assumed to be steno dictionary files.
    SpectraGUIQtApplication(files=sys.argv[1:])


if __name__ == '__main__':
    main()
