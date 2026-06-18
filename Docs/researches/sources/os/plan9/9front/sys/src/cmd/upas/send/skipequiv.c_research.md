# File Research: sources/os/plan9/9front/sys/src/cmd/upas/send/skipequiv.c

`skipequiv()` removes leading bang-path systems found in `/mail/lib/equivlist`. It tokenizes the equivlist as whitespace/comma-separated names, caches the opened file, and repeatedly advances past matching path components.

The function temporarily writes NULs into the input string while testing each component, then restores `!`. It returns a pointer into the original string rather than allocating.
