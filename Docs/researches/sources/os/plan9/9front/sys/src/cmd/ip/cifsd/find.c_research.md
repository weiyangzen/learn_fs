# File Research: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/find.c

Implements SMB directory search state and wildcard matching.

Key points:
- `iswild` detects SMB wildcard characters `*?<>\"`.
- `matchpattern` implements SMB wildcard semantics:
  - `?` matches one rune.
  - `*` and `<` match variable spans with DOS dot handling.
  - `>` has DOS special behavior around dot/end.
  - `"` matches dot or end.
  - case-insensitive matching uses rune uppercase comparison.
- `matchattr` filters entries by DOS file attributes and search mask.
- `openfind` splits search path into base/pattern, reads a directory for wildcard searches, or stats an exact path for non-wildcard searches.
- Optional `withdot` adds synthetic/current `.` and parent `..` stats.
- `readfind` scans from an index to the next matching `Dir`.
- `putfind` releases directory, dot/dotdot, pattern, and base state.

Dependencies and interactions:
- Uses `xdirread`, `xdirstat`, `splitpath`, `dosfileattr`, and name comparison functions.
- `Find` objects are stored in tree search-id tables.

Research relevance:
- Implements Windows/SMB-style directory enumeration semantics over Plan 9 directories.
