# File Research: sources/os/plan9/plan9/sys/src/cmd/mk/match.c

Implements pattern matching and substitution for non-regexp meta rules.

Key functions:
- `match(name, template, stem)` matches templates containing `%` or `&`.
- `subst(stem, template, dest, dlen)` substitutes stem into templates at `%` or `&`.

Behavior notes:
- `&` is stricter than `%`: matched stem must not contain `.` or `/`.
- Matching checks literal prefix before wildcard and literal suffix after wildcard.
- Substitution is bounded by destination length and null-terminates output.
