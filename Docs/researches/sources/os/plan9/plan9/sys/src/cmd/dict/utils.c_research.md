# File Research: sources/os/plan9/plan9/sys/src/cmd/dict/utils.c

Shared support for the Plan 9 `dict` command backends.

`dicts[]` is the central registry mapping dictionary names to descriptions, data paths, index paths, and callback triplets. It registers OED, AHD, Webster, thesaurus, Roget, world-language dictionaries, Collins variants, Russian simple dictionaries, movies, slang, and Robert data.

The file defines shared ligature and multi-rune expansion tables. `ligtab` maps private-use accent codes from `dict.h` to accent runes and base/accented rune pairs. `multitab` maps private-use multi-character codes to rune strings such as ligatures, Greek breathing combinations, `and`, `or`, and em-space approximations.

Utility APIs include sorted association binary searches (`lookassoc`, `looknassoc`), formatted diagnostics (`err`), output wrappers (`outrune`, `outchar`, `outchars`, `outprint`, `outpiece`, `outnl`) that respect `outinhibit` and `breaklen`, rune folding for search (`fold`, `foldre`), accent-insensitive comparison helper `acomp`, rune copy and numeric conversion helpers, `liglookup`, and `changett` for a stack of translation tables.

Integration points: every dictionary backend depends on this file for output normalization, line wrapping, tag/entity lookup, fold/search behavior, and callback registration.

Risks and notes: global output state (`linelen`, `outinhibit`, `breaklen`, `debug`) makes callbacks non-reentrant. `changett` has a fixed stack depth of 20 and debug-only overflow/underflow handling. Accent/multi-rune handling is table-driven and intentionally approximate for some source glyphs.
