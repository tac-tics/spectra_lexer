import sys

from .base import CORE
from .engine import Engine
from .group import InstanceGroup
from .main import main


class Application(CORE):
    """ Abstract base application class for the Spectra program. The starting point for program logic. """

    DESCRIPTION: str = "Spectra program."  # Program description as seen in the command line help.

    _components: InstanceGroup

    def __init__(self):
        """ Build the components and assemble the engine with them to get a top-level callable. """
        self._components = InstanceGroup(self._class_paths(), whitelist=CORE, blacklist=Application)
        self._engine(exc_command=CORE.Exception).connect(self)

    def _class_paths(self) -> list:
        """ Return a list of modules or classes to draw components from.
            For multi-threaded applications, there may be a separate list for each thread. """
        raise NotImplementedError

    def _engine(self, **kwargs) -> Engine:
        """ Make and return a new engine; may differ for subclasses. """
        return Engine(self._components, **kwargs)

    def start(self) -> int:
        self.Load()
        return self.run()

    def run(self) -> int:
        """ After everything else is ready, a primary task may be run. It may return an exit code to main().
            A batch operation can run until complete, or a GUI event loop can run indefinitely. """
        raise NotImplementedError

    def Exit(self) -> None:
        """ A worker thread calling sys.exit will not kill the main program, so it must be done here. """
        sys.exit()

    @classmethod
    def set_entry_point(cls, mode:str, **kwargs) -> None:
        """ Make an entry point for this application class and add it to the main dict. """
        main.add_entry_point(cls.app_main, mode, cls.DESCRIPTION, **kwargs)

    @classmethod
    def app_main(cls, *args, **kwargs) -> int:
        """ Create the application, run it, and return an exit code. """
        return cls(*args, **kwargs).start()
