# File Research: sources/os/plan9/plan9/sys/src/cmd/rc/glob.c

Filename globbing and pattern matching for rc.

Main pieces:
- `deglob()` removes internal `GLOB` escape markers.
- `glob()` expands one pattern, falling back to literal text if no matches.
- `globdir()` recursively scans path components, opening directories only at components containing glob metacharacters.
- `globsort()` sorts matched names lexicographically.
- UTF helpers `equtf()`, `nextutf()`, `unicode()` keep matching rune-aware.
- `matchfn()` applies filename-specific dotfile rules.
- `match()` implements `*`, `?`, character classes, ranges, complements, and escaped `GLOB`.
- `globlist()` expands every word on the current argv list.

Risk/notes:
- Glob metacharacters are represented as `GLOB` followed by the actual metacharacter.
- `.` and `..` only match patterns beginning with `.`.
- Directory-only hints are passed to `Readdir()` when the remaining pattern contains `/`.
