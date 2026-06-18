# File Research: sources/os/plan9/9front/sys/src/cmd/htmlroff/char.c

Maps troff two-character special names to Unicode runes.

Key points:
- Maintains a static translation table initialized on first use.
- Seeds translations for plus/equal/minus symbols, em/en dashes, and prime.
- Reads `/sys/lib/troff/font/devutf/utfmap` to populate additional troff escape mappings.
- `troff2rune` accepts a two-rune troff name and returns the mapped Unicode rune or `Runeerror`.
- Warns if the fixed translation table fills.

Dependencies and interactions:
- Used by `t2.c` for `\(` special character escapes.
- Uses Plan 9 `Biobuf`, `getfields`, and UTF conversion routines.

Research relevance:
- This avoids duplicating troff character maps in source and ties `htmlroff` output to the system troff font mapping.
