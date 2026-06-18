# File Research: sources/os/plan9/9front/sys/src/cmd/rc/glob.c

Implements `rc` glob expansion and pattern matching. Uses an internal `GLOB` marker inserted by the lexer before glob metacharacters.

`globword()` replaces a word in-place with sorted filesystem matches; unmatched words are deglobbed literally. `globdir()` recursively opens directories and filters entries, with Plan 9-specific directory-only filtering for intermediate slash components.

`match()` is UTF-aware and supports `*`, `?`, character classes/ranges, complement classes with `~`, and stop characters such as `/`. It avoids matching `.` and `..` unless the pattern starts with `.`.
