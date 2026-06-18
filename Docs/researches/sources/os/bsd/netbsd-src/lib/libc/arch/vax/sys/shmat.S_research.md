# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/vax/sys/shmat.S

## Summary
Provides VAX `shmat()` syscall wrapper.

## Key Details
- Includes `SYS.h`.
- Expands `RSYSCALL(shmat)`.

## Notes
The wrapper uses the standard VAX syscall macro path.
