# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/stub.c

Minimal 9P filesystem that inserts a single stub child into a mount point. It can expose one empty file or one empty directory.

Core behavior:
- `aux/stub [-Dd] path/name`.
- Splits `path/name` into mount point and child name.
- Mounts a 9P server `MBEFORE` at the parent path.
- Root directory lists exactly one entry.
- `-d` makes the child a directory.
- Non-root open is denied; root may be opened read-only.
- Writes always fail with `no writing`.

Important functions:
- `fsattach()`, `fswalk1()`, `fsstat()`, `fsread()`, `fsopen()`.
- `dirgen()` supplies the single directory entry for `dirread9p()`.

Dependencies and integration:
- Uses Plan 9 thread and `<9p.h>` server library.
- Closes standard descriptors before mounting to avoid confusing `mk`.

Notable risks:
- Child file has no read implementation beyond root directory listing; opening it is denied.
- `kidmode` defaults to 0 for file mode unless `-d`; that produces a file with no permission bits.
