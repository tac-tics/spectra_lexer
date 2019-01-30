""" Module for the lowest-level string and list operations. Performance is more critical than readability here. """

from operator import itemgetter
from typing import List


class TaggedGrid(List[list]):
    """ A mutable 2D grid-like structure that has metadata tag objects associated with characters.
        For performance, the implementation is low-level: each row is a list with alternating characters and tags.
        list.__init__ should not be overridden; this will facilitate fast list copying. No bounds checking is done.
        Operations on the document as a whole may span multiple rows, and should be optimized for map(). """

    _BLANKS_CACHE: dict = {}  # Cache of blank lines of various sizes for fast copying.

    def memcpy(self, grid:List[list], row:int=0, col:int=0, _zip=zip, _len=len) -> None:
        """ Copy the contents of one grid directly to this one at the given offset. """
        col *= 2
        for r, line in _zip(self[row:], grid):
            r[col:col+_len(line)] = line

    def write(self, grid:List[str], tag:object=None, row:int=0, col:int=0, _zip=zip) -> None:
        """ Copy a list of strings with a single tag to this one at the given offset. """
        for r, s in enumerate(grid, row):
            self.write_row(s, tag, r, col)

    def write_row(self, s:str, tag:object=None, row:int=0, col:int=0, _len=len) -> None:
        """ Like write(), but writes a single string and tag to any row in the grid.
            This is the most performance-critical method in graphing, called hundreds of times per frame.
            Avoid method call overhead by inlining everything and using slice assignment over list methods. """
        r = self[row]
        col *= 2
        under = col - _len(r)
        if under > 0:  # if shorter than start position, pad with spaces and None tags.
            r.extend([" ", None] * (under // 2))
        length = _len(s)
        if length == 1:  # fast path: <s> is a one character string.
            r[col:col+2] = [s, tag]
            return
        length *= 2  # slow path: <s> is a arbitrarily long standard string.
        end = col + length
        r[col:end] = [tag] * length
        r[col:end:2] = s

    def write_column(self, s:str, tag:object=None, row:int=0, col:int=0, _zip=zip) -> None:
        """ Like write(), but writes the string down a column instead of across a row.
            This is much slower because a different list must be accessed and written for every character. """
        col *= 2
        end_col = col + 2
        for r, c in _zip(self[row:], s):
            r[col:end_col] = [c, tag]

    @classmethod
    def blanks(cls, rows:int, cols:int, _cache_get=_BLANKS_CACHE.get) -> List[list]:
        """ Make a new, blank grid consisting of spaces and None references. Rows can be cached for speed. """
        line = _cache_get(cols)
        if line is None:
            line = [" ", None] * cols
            cls._BLANKS_CACHE[cols] = line
        return cls(map(list, [line] * rows))

    @property
    def size(self, _len=len) -> tuple:
        """ Return the size of the grid in (rows, cols). Overall column size is determined by the longest one. """
        return _len(self), max(map(_len, self)) // 2

    def row_str_op(self, row:int, op:callable, *args, _join="".join) -> None:
        """ Do an in-place string operation on a row without altering any tags. """
        self[row][::2] = op(_join(self[row][::2]), *args)

    def compile_strings(self, _chars=itemgetter(slice(0, None, 2)), _join="".join) -> List[str]:
        """ De-interleave the string data from each tagged string to form a list of strings. """
        return list(map(_join, map(_chars, self)))

    def compile_tags(self, _tags=itemgetter(slice(1, None, 2))) -> List[list]:
        """ De-interleave the tag data from each tagged string to form a list of lists or 2D grid of tags. """
        return list(map(_tags, self))
