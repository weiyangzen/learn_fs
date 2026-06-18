# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/mkindex.c

This file implements `mkindex`, a helper for producing raw dictionary indexes.

Key behaviors:
- Selects a dictionary backend with `-d`; defaults to `dicts[0]`.
- Supports `-D` for debug.
- Opens the dictionary data file and walks entries from offset 0 to EOF using the backend `nextoff()`.
- For each entry, prints `offset<TAB>` and then invokes the backend `printentry(e, 'h')` to emit headwords.
- Uses a very large `breaklen` to keep headword output on one line.
- `getentry()` materializes an entry from offset `b` to the next backend offset, falling back to EOF for the last entry.

Notable implementation details:
- The output is intended for later sorting and canonicalization into the index format consumed by `dict`.
- Shares global names expected by backend print functions: `bdict`, `bout`, `linelen`, `breaklen`, `outinhibit`, and `debug`.
