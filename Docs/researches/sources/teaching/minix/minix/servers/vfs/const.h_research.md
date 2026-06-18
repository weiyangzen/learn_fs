# File Research: sources/teaching/minix/minix/servers/vfs/const.h

Core VFS constants.

Defines:
- Table sizes: `NR_FILPS`, `NR_LOCKS`, `NR_MNTS`, `NR_VNODES`, `NR_WTHREADS`, `NR_SOCKDEVS`.
- Special UID/GID values for system and superuser.
- Process blocking states:
  - none
  - pipe
  - flock
  - pipe open
  - select
  - character device I/O
  - socket I/O
- `fp_is_blocked` helper macro.
- `INVALID_THREAD`.
- `SYMLOOP`.
- Label and filesystem type name limits.
- Select operation aliases shared with CDEV/SDEV constants.
- Compile-time check that CDEV and SDEV select constants match.
- `CTTY_ENDPT`, the synthetic endpoint for `/dev/tty` handling inside VFS.
