# File Research: sources/teaching/xv6-riscv/kernel/fcntl.h

Defines open flags used by `sys_open()`:
- `O_RDONLY`
- `O_WRONLY`
- `O_RDWR`
- `O_CREATE`
- `O_TRUNC`

Filesystem relevance: these constants control file creation, read/write permissions, directory open restrictions, and truncation behavior in `sysfile.c`.
