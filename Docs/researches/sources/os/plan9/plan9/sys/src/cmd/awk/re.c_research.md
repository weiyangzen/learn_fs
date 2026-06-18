# File Research: sources/os/plan9/plan9/sys/src/cmd/awk/re.c

Awk-facing regular expression adapter.

It preprocesses awk regex syntax before handing patterns to Plan 9 regexp routines. Conversions include empty regex constructs, character-class edge cases, octal/hex escapes, and common escapes like `\n`, `\t`, and `\b`.

Key functions:

- `compre()`: preprocesses and compiles regexes; caches up to 20 dynamic runtime patterns.
- `match()`: boolean match.
- `pmatch()`: match and export `patbeg`/`patlen`.
- `nematch()`: non-empty match helper for field splitting.
- `quoted()` and `hexstr()`: escape parsing.
- `countposn()`: multibyte/rune position counting for awk-visible positions.
- `regerror()`/`overflow()`: fatal regexp error paths.
