# File Research: sources/os/plan9/9front/sys/src/cmd/look.c

`look` searches a sorted text file, defaulting to `/lib/words`, for entries matching a key or keys from stdin. It supports dictionary-style canonicalization, case folding, exact matching, alternate tab field delimiter, and numeric comparison.

Key behavior:
- Converts UTF-8 arguments/input to Rune arrays.
- `rcanon()` canonicalizes by stopping at a tab, optional directory mode, optional case fold, and Latin-1 accent folding to ASCII approximations.
- `locate()` binary-searches the file to the first possible match, then scans forward.
- `acomp()` performs prefix-aware lexicographic comparison.
- `ncomp()` performs numeric comparison with sign, integer, and fractional handling under configurable base.
- `getword()` reads Rune lines through Bio.

The implementation assumes sorted input according to the selected comparison/canonicalization mode.
