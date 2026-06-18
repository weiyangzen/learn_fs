# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/dict.c

This file is the main Plan 9 `dict` command implementation.

Key behaviors:
- Selects the first installed dictionary from `dicts[]`, or one named by `-d`.
- Supports `-k` to print the dictionary’s key, `-c` to run one command, `-D` for debug, and a single word argument as shorthand for `/word/P`.
- Opens dictionary and index files and tracks `dot`, the current address set.
- Command parser accepts addresses followed by commands:
  - `a`: print address.
  - `h`: headword/brief output.
  - `p`: formatted entry.
  - `r`: raw-ish entry where dictionary backend supports it.
  - Uppercase commands operate over all matches.
- Address parser supports:
  - `/re/`: folded anchored regex.
  - `!re!`: non-folded anchored regex.
  - `#offset`: absolute dictionary byte offset.
  - numeric result selector.
  - `.` current result.
  - `+`/`-` next/previous entry motion.
- `search()` uses folded prefixes to binary-search the sorted index, then scans matching index lines, regex-filtering if needed.
- `locate()` performs binary search in the index file and then a linear correction pass.
- `getentry()` materializes an entry by asking the active dictionary for the next entry offset.

Notable implementation details:
- Index format is `key<TAB>dictionary_offset`.
- Search results are sorted and uniqued by `sortaddr()`.
- `setdotprev()` searches backward by widening a lookback window and repeatedly using the backend `nextoff()`.
- The main command loop is interactive and prompts with `*`.
