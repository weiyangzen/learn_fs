# File Research: sources/os/plan9/9front/sys/src/cmd/mk/match.c

Implements mk’s simple `%` and `&` meta-rule matching and substitution.

Key behavior:
- `match()` checks literal prefix/suffix around the first `%` or `&`, extracts the stem, and rejects `&` stems containing `.` or `/`.
- `subst()` copies a template to a destination buffer, replacing `%` or `&` with the stem.

Important dependencies: `mk.h`, `PERCENT`, UTF rune scanning.

Notable risks:
- Only one meta marker is effectively supported.
- `subst()` truncates silently to `dlen - 1`.
