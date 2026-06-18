# File Research: sources/os/plan9/9front/sys/src/cmd/gefs/dump.c

Debug formatting and recursive block/tree dump support for gefs.

Key responsibilities:
- Implements custom formatters for block pointers, messages, key/value pairs, keys, qids, and arena ranges.
- Decodes gefs key/value types into readable text for data pointers, dirents, snapshot labels/roots, parent links, deadlists, and config.
- Recursively prints leaf and pivot blocks, including pivot buffers and child pointers.
- Provides `showblk()`, `showbp()`, `showtreeroot()`, and `initshow()` for console/debug use.

Important behavior:
- `%#P` and `%#M` treat values as block pointers with fill counts.
- `showval()` decodes `Owstat`, snapshot relinks, deadlist heads/tails, and serialized `Xdir` fields.
- `rshowblk()` follows child pointers when recursion is enabled.

Notable risks:
- Recursive tree dump calls `getblk()` on child pointers and can be expensive or fail on corrupt structures.
- Some formatting paths abort on malformed sizes rather than returning a printable error.
