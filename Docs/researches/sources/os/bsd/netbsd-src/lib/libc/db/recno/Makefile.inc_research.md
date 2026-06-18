# File Research: sources/os/bsd/netbsd-src/lib/libc/db/recno/Makefile.inc

Build fragment for the recno access method. It adds `${.CURDIR}/db/recno` to `.PATH` and appends close, delete, get, open, put, search, sequence, and utility implementation files to `SRCS`.

Dependencies: recno builds on the btree implementation and includes btree private headers.

Risks/invariants: source list must remain synchronized with private prototypes in `recno/extern.h`.
