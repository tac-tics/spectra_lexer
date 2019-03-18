from typing import Sequence

from spectra_lexer import Component


class FileDialogTool(Component):
    """ Controls user-based file loading and window closing. This should not be loaded in plugin mode. """

    load_rules = Option("menu", "File:Load Rules...", ["file_dialog_open", "rules"])
    load_translations = Option("menu", "File:Load Translations...", ["file_dialog_open", "translations"])
    load_index = Option("menu", "File:Load Index...", ["file_dialog_open", "index"])
    sep = Option("menu", "File:")
    close_window = Option("menu", "File:Exit", ["gui_window_close"])

    @on("file_dialog_open", "new_dialog")
    def open_dialog(self, res_type:str) -> tuple:
        """ Present a dialog for the user to select files of a specific resource type. """
        title_msg = f"Load {res_type.title()}"
        fmts_msg = "Supported file formats"
        fmts = self.engine_call("file_get_extensions")
        return f"{res_type}-file", title_msg, fmts_msg, fmts

    @on("file_dialog_result")
    def load(self, res_type:str, filenames:Sequence[str]=()) -> None:
        """ Attempt to load the given files (if any) as the last resource type. """
        if filenames:
            self.engine_call("new_status", f"Loading {res_type}...")
            self.engine_call(f"{res_type}_load", filenames)
            self.engine_call("new_status", f"Loaded {res_type} from file dialog.")