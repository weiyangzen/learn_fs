# File Research: sources/os/plan9/plan9/sys/src/cmd/htmlroff/char.c

Character translation helpers for `htmlroff`.

- `rune2html()` converts Unicode runes to HTML by spawning `/bin/tcs -t html`, sending runes through a pipe, and caching per-rune results in a two-level cache.
- Handles newline directly and rejects runes outside 16-bit range due to cache shape.
- `troff2rune()` maps two-character troff special names to Unicode runes.
- Initializes a small built-in troff mapping table, then loads `/sys/lib/troff/font/devutf/utfmap`.

Dependencies are `/bin/tcs`, troff `utfmap`, Plan 9 `bio`, pipes/fork/exec, and `a.h`.

Notable concerns: `rune2html()` depends on a long-lived external `tcs` process and uses extra newlines as a flushing hack. `trtab` has a fixed size of 200 entries and warns if too small.
