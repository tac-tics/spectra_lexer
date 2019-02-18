from time import time

from spectra_lexer.app import SpectraApplication
from spectra_lexer.batch import BatchExecutor


def main() -> None:
    """ Top-level function for operation of the Spectra program by itself in batch mode. """
    # The script will exit after processing all <translations> and saving the rules to <out>.
    s_time = time()
    app = SpectraApplication(BatchExecutor)
    app.start(translations=(), out="output.json", processes=None)
    print("Processing done in {:.1f} seconds.".format(time() - s_time))


if __name__ == '__main__':
    main()
