# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/cygwin.c

Cygwin compatibility shims for u9fs.

Functions:
- `pread` and `pwrite` emulate positional I/O with `lseek`, preserving/restoring the original file offset and `errno`.
- `setreuid` maps requested real/effective uid changes to `setuid`/`seteuid`.
- `setregid` maps requested real/effective gid changes to `setgid`/`setegid`.

Notable issue:
- `setreuid` and `setregid` have no explicit success return at the end, despite returning `int`.
