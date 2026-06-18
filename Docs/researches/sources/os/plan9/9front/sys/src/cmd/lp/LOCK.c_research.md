# File Research: sources/os/plan9/9front/sys/src/cmd/lp/LOCK.c

This helper creates an exclusive lock file for the printer subsystem, writes `hostname ppid`, forks, and lets the parent exit while the child keeps the lock alive.

The child periodically stats and zero-byte writes the file until the file disappears, becomes zero-length, or write/stat fails. It then closes the fd and sends `kill` to the supplied parent process group.

It is a specialized Plan 9 printer lock keeper using `DMEXCL` files and notes.
