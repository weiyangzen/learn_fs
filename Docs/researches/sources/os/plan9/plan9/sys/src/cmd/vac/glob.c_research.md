# File Research: sources/os/plan9/plan9/sys/src/cmd/vac/glob.c

Purpose: include/exclude pattern engine for the `vac` archiver.

Key behavior:
- `glob2regexp` converts a Vac glob syntax into a Plan 9 regular expression.
- Supported patterns include `*`, `...`, `?`, bracket classes, and `~` negation inside bracket classes.
- Beginning-of-path-element handling prevents leading `.` matches for `*`/`?` unless explicitly requested.
- `loadexcludefile` reads lines beginning with `include ` or `exclude `, skips blank/comment lines, compiles patterns, and stores ordered rules.
- `excludepattern` appends a command-line exclusion rule.
- `includefile` returns the first matching rule’s include flag, defaulting to included.

Integration points:
- Used by `vac.c` to skip files during archive creation.
- Tested interactively by `testinc.c`.

Risks:
- Pattern storage is global and append-only.
- `glob2regexp` allocates `20 * strlen(glob)` bytes, which is generous but assumes the expansion bound remains true.
- Character-class parsing walks until `]`; malformed classes reach syntax handling through failed compilation or slash checks.
