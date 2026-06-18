# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbrep.c

SMB wildcard pattern to Plan 9 regexp conversion and matching.

Key functions:
- `smbmkrep` translates `*`, `*.`, `?`, repeated `?`, and regexp metacharacters into a regexp string, compiles it, and logs optional conversion.
- `smbmatch` checks that a regexp matches an entire file name.

Interactions:
- Used by wildcard delete and likely directory search code.

Notable details:
- `?` behavior differs at end or before dot: it becomes optional non-dot match.
