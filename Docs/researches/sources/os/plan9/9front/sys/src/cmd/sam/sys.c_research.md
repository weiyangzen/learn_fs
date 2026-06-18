# File Research: sources/os/plan9/9front/sys/src/cmd/sam/sys.c

`sys.c` provides guarded wrappers around system calls used by sam.

`resetsys` clears the local reentrancy guard. `syserror` captures the current error string, prints the failing operation, and raises an `Eio` sam error once, avoiding recursive error storms.

`Read` requires an exact byte count. On short read or error it marks `lastfile` as rescuing, reports the read error in downloaded mode, runs `rescue`, and exits.

`Write` requires an exact write and reports via `syserror` otherwise. `Seek` wraps `seek` and raises `syserror` on failure.
