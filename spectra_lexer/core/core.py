import sys
from traceback import TracebackException
from typing import List

from .base import CORE
from .cmdline import CmdlineOption
from .console import SystemConsole
from .io import PathIO
from .log import StreamLogger


class SpectraCore(CORE):
    """ Component for handling the command line, console, files, and logging engine status and exceptions. """

    log_file: str = CmdlineOption("log-file", default="~/status.log",
                                  desc="Text file to log status and exceptions.")

    _io: PathIO            # Reads, writes, and converts path strings.
    _logger: StreamLogger  # Logs system events to standard streams and/or files.
    _components: list      # Contains every component definition in the application.
    _console: SystemConsole = None

    def __init__(self):
        self._io = PathIO(**self.get_root_paths())
        self._logger = StreamLogger(sys.stdout)
        self._components = [self]

    def Load(self) -> None:
        log_path = self._io.to_path(self.log_file)
        self._logger.add_path(log_path)

    def COREDebug(self, components:list) -> None:
        self._components = components

    def COREConsoleOpen(self, *, interactive:bool=True, **kwargs) -> None:
        kwargs["__app__"] = self._components
        self._console = SystemConsole(self.SYSConsoleOutput, interactive, self.CONSOLE_COMMANDS, **kwargs)

    def COREConsoleInput(self, text_in:str) -> None:
        if self._console is not None:
            self._console.run(text_in)

    def COREFileLoad(self, *patterns:str, **kwargs) -> List[bytes]:
        return [*self._io.read(*patterns, **kwargs)]

    def COREFileSave(self, data:bytes, filename:str) -> None:
        self._io.write(data, filename)

    def COREStatus(self, status:str) -> None:
        """ Log and print status messages to stdout by default. """
        self._logger(status)

    def COREException(self, exc:Exception, max_frames:int=10) -> bool:
        """ Log and print an exception traceback to stdout, if possible. """
        tb = TracebackException.from_exception(exc, limit=max_frames)
        tb_text = "".join(tb.format())
        self._logger(f'EXCEPTION\n{tb_text}')
        return True

    @classmethod
    def get_root_paths(cls) -> dict:
        """ The name of this class's root package is used as a default path for built-in assets and user files. """
        root_package = cls.__module__.split(".", 1)[0]
        return {"asset_path": root_package,  # Root directory for application assets.
                "user_path":  root_package}  # Root directory for user data files.