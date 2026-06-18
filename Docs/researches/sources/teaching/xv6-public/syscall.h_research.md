# File Research: sources/teaching/xv6-public/syscall.h

Defines numeric system call IDs.

Includes:
- Process calls: `fork`, `exit`, `wait`, `kill`, `getpid`, `sbrk`, `sleep`, `uptime`.
- File/FS calls: `pipe`, `read`, `write`, `open`, `close`, `fstat`, `chdir`, `dup`, `mknod`, `unlink`, `link`, `mkdir`.
- `exec`.

Shared by kernel dispatcher, user syscall stubs, and `initcode.S`.
