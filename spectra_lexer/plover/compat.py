""" Module to hold all compatibility-related code for Plover, including partial class typedefs and version check. """

from typing import Callable, Iterable, Optional, Sequence, Tuple

import pkg_resources

from spectra_lexer import Component
from spectra_lexer.utils import nop

# Minimum version of Plover required for plugin compatibility.
_PLOVER_VERSION_REQUIRED = "4.0.0.dev8"
INCOMPATIBLE_MESSAGE = f"ERROR: Plover v{_PLOVER_VERSION_REQUIRED} or greater required."
# Key constants and functions for Plover stroke strings.
PLOVER_SEP = "/"
join_strokes = PLOVER_SEP.join

# Partial class structures that specify a minimum type interface for compatibility with Plover.
# There is enough init code with default parameters to allow tests by creating a fake engine.
class PloverStenoDict:
    enabled: bool = True
    def __init__(self, d:dict):
        self._dict = dict(zip(map(tuple, [k.split(PLOVER_SEP) for k in d]), d.values()))
    def items(self) -> Iterable[tuple]:
        return self._dict.items()
    def __len__(self) -> int:
        return len(self._dict)

class PloverStenoDictCollection:
    dicts: Iterable[PloverStenoDict] = [PloverStenoDict({"TEFT": "test", "TE*S": "test", "TEFGT": "testing"})]
    def __init__(self, d:dict=None, split_count:int=1):
        if d is not None:
            d_list = list(d.items())
            self.dicts = [PloverStenoDict(dict(d_list[i::split_count])) for i in range(split_count)]

class PloverAction:
    prev_attach: bool = True
    text: Optional[str] = "Plover Test"

class PloverTranslation:
    rtfcre: Tuple[str] = ("PHROFR", "TEFT")
    english: Optional[str] = "Plover Test"

class PloverTranslatorState:
    translations: Sequence[PloverTranslation] = [PloverTranslation()]

class PloverEngine:
    dictionaries: PloverStenoDictCollection = PloverStenoDictCollection()
    translator_state: PloverTranslatorState = PloverTranslatorState()
    signal_connect: Callable[[str, Callable], None] = nop
    __enter__: Callable[[], None] = nop
    __exit__: Callable[..., None] = nop


class PloverCompatibilityLayer(Component):
    """ Simple component for specific compatibility checks and tests on Plover's version number and data types. """

    @on("plover_test")
    def test(self) -> None:
        """ Make a fake Plover engine and run some simple tests. """
        self.engine_call("new_plover_engine", PloverEngine())
        self.engine_call("plover_new_translation", None, [PloverAction()])

    @on("plover_connect")
    def connect(self, plover_engine:PloverEngine) -> None:
        """ Connect the Plover engine to ours only if a compatible version of Plover is found. """
        if _compatibility_check():
            self.engine_call("new_plover_engine", plover_engine)
        else:
            # If the compatibility check fails, don't try to connect to Plover. Send an error.
            self.engine_call("new_status", INCOMPATIBLE_MESSAGE)


def _compatibility_check() -> bool:
    """ Return True only if a compatible version of Plover is found in the working set. """
    try:
        pkg_resources.working_set.require("plover>=" + _PLOVER_VERSION_REQUIRED)
        return True
    except pkg_resources.ResolutionError:
        return False
