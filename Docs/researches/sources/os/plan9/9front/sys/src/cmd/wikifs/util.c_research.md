# File Research: sources/os/plan9/9front/sys/src/cmd/wikifs/util.c

Shared allocation, string, substitution, append-list, and temp-file helpers for `wikifs`.

Key behavior:
- `emalloc()`/`erealloc()` abort on allocation failure, zero new allocations, and tag allocations.
- `estrdup()` and `estrdupn()` duplicate nullable or bounded strings.
- `strlower()` lowercases ASCII letters in place.
- `s_appendsub()` appends text while replacing the earliest matching substitution tokens.
- `s_appendlist()` appends a nil-terminated list of strings to a `String`.
- `opentemp()` repeatedly applies `mktemp()`, creates an `ORCLOSE` temp file, and writes the chosen path back to the template.

Notable dependencies:
- Plan 9 String library and libc file APIs.

Research notes:
- `s_appendsub()` only considers substitutions whose replacement string is non-nil.
