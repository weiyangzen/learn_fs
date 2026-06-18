# File Research: sources/os/plan9/9front/sys/src/cmd/dict/utils.c

Shared dictionary registry and utility layer.

Key elements:
- Defines `dicts[]`, mapping dictionary names to descriptions, data/index paths, and callbacks.
- Registers OED, AHD, PGW, thesaurus, Roget, world-language dictionaries, Collins variants, Russian simple dictionaries, movie indexes, slang, and Robert variants.
- Defines accent ligature tables and multi-rune expansion tables.
- Provides binary search helpers `lookassoc` and `looknassoc`.
- Provides common diagnostics and output functions with line wrapping and indentation.
- Implements folding for ASCII uppercase and Latin-1 accented characters.
- Implements regex string folding for search.
- Defines `acomp` prefix-aware comparison used by index search.
- Implements `runetol`, `liglookup`, and a translation-table stack `changett`.

Dependencies:
- Central dependency for nearly every dictionary adapter.
- Uses globals declared in `dict.h` and owned by `dict.c` or `mkindex.c`.

Research notes:
- `dicts[]` is both runtime configuration and backend registry.
- Output helpers intentionally collapse or wrap text for terminal readability.
