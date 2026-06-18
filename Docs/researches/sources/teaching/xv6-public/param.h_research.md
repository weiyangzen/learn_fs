# File Research: sources/teaching/xv6-public/param.h

Global xv6 sizing constants.

Defines:
- Process, CPU, file descriptor, file table, inode, device, argument, log, buffer, kernel stack, and filesystem-size limits.
- Root device number.
- `LOGSIZE` and `NBUF` derived from `MAXOPBLOCKS`.

Role:
- Central tuning point for resource limits used by kernel and tools.
