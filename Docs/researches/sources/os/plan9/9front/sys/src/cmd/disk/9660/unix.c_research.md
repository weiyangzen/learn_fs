# File Research: sources/os/plan9/9front/sys/src/cmd/disk/9660/unix.c

Unix host adapter for ISO image building.

Key behavior:
- `dirtoxdir` converts `Dir` to `XDir`, resolves numeric uid/gid via `getpwnam`/`getgrnam`, and preserves symlink targets when `CHLINK` is set.
- `fdtruncate` calls POSIX `ftruncate`.
- `numericuid` and `numericgid` warn once if user/group lookup fails and return zero.

Notable dependencies:
- `<pwd.h>`, `<grp.h>`, and Plan 9 compatibility headers.

Research notes:
- Provides host-specific behavior needed when building the tools outside native Plan 9.
