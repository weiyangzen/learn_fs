# File Research: sources/os/plan9/9front/sys/src/cmd/dict/dict.c

Interactive and command-line front end for the Plan 9 `dict` command.

Key elements:
- Selects the first installed dictionary from `dicts[]`, or a named one via `-d`.
- Supports `-k` pronunciation key printing, `-c cmd`, debug `-D`, and a shorthand positional search pattern.
- Maintains `dot`, an address set of dictionary byte offsets with current selection.
- Parses commands `a`, `h`, `p`, `r` and uppercase all-entry variants.
- Address syntax includes current `.`, regex `/.../`, non-folding regex `!...!`, result number, absolute dictionary offset `#n`, and `+`/`-` entry navigation.
- Searches the sorted index by extracting a literal prefix, binary-locating it in the folded index, then regex/filtering matching entries.
- `getentry` reads an entry by using the active dictionary `nextoff` callback to find its end.
- `setdotprev` scans backward heuristically by expanding a previous search window and repeatedly calling `nextoff`.

Dependencies:
- Uses `Dict` callbacks from `dict.h`/`utils.c`.
- Uses Plan 9 `Biobuf`, `regexp`, `ARGBEGIN`, rune APIs, and `qsort`.
- Relies on index records of `key<TAB>offset`, sorted by folded key plus numeric offset.

Research notes:
- Case-folded search is intentionally aligned with `sort(1)` folding for dictionary indexes.
- Prefix search is a performance optimization: it avoids scanning the whole index for anchored regexes.
- Uppercase commands iterate over all current matches; lowercase commands operate on `dot->cur`.
