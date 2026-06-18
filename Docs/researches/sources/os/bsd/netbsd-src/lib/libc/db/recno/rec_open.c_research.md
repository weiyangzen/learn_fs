# File Research: sources/os/bsd/netbsd-src/lib/libc/db/recno/rec_open.c

Opens a recno database by wrapping a btree. `__rec_open` optionally opens the user's record file, creates a btree backing store with `__bt_open`, copies recno options into the `BTREE` state, marks the tree as `R_RECNO`, selects fixed or variable record handling, and installs recno DB method pointers.

For named files it handles read-only versus read/write modes, detects non-seekable input via `lseek`/`ESPIPE`, and uses a `FILE *` reader for pipe-like sources. The mmap path is present but compiled out unless `MMAP_NOT_AVAILABLE` is defined in a way that enables it; otherwise regular files also use the slow `FILE *` path. The root page is converted from `P_BLEAF` to `P_RLEAF`. `R_SNAPSHOT` forces import of the full backing file at open.

`__rec_fd` returns the backing record file descriptor and rejects in-memory recno databases with `ENOENT`.

Risks/invariants: recno uses btree storage but changes page type and method table after open. Some flag combinations are rejected with `EINVAL`, especially writable pipe-like inputs.
