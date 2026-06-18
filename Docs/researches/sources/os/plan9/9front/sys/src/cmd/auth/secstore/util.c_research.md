# File Research: sources/os/plan9/9front/sys/src/cmd/auth/secstore/util.c

Small shared utility file for secstore components.

Functions:
- `emalloc()` allocates zeroed memory or exits via `sysfatal`.
- `erealloc()` reallocates or exits.
- `estrdup()` duplicates strings or exits.
- `validatefile()` accepts only simple non-empty filenames, rejecting `".."`, names length >= 250, control characters, and `/`.
- `illegal()` logs rejected names to the secstore syslog.

Filesystem relevance:
- `validatefile()` is the server-side guard preventing secstore protocol filenames from escaping per-user directories.
