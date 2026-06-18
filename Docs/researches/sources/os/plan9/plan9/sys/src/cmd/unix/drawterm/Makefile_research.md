# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/Makefile

Read fully: 75 lines, 1165 bytes. SHA-256 prefix: `067ab30d37cd2be9`.

This is the top-level drawterm makefile. It includes `Make.config`, builds object files for main CPU/readconsole/secstore/factotum support, and links a large set of static Plan 9 compatibility libraries.

Key targets:
- `$(TARG)` links `$(OFILES)` with repeated `$(LIBS1)` and `libmachdep.a`.
- Pattern rule compiles `%.c` to `%.$O`.
- `clean` removes object archives and drawterm binaries.
- Recursive targets build `kern`, `exportfs`, auth/authsrv, crypto/math, memdraw/memlayer/draw, GUI backend, libc, and libip.

Risk notes: comment “stupid gcc” explains repeating libraries to satisfy link ordering.
