# File Research: sources/os/plan9/plan9/sys/src/cmd/lp/LOCK.c

Read fully: 57 lines, 1066 bytes. SHA-256 prefix: `9af1d14a501a58de`.

This helper creates and maintains an exclusive printer lock file. It expects `LOCK lockfile hostname ppid`, creates the lock file with `DMEXCL`, writes `hostname ppid`, forks, and lets the parent exit successfully while the child keeps the lock alive. The child polls file status and zero-length writes until the file disappears, empties, or write fails, then posts a kill note to the parent process group.

Integration: intended for the lp subsystem’s queue/daemon locking workflow.

Risk notes: kill behavior targets the supplied parent process group. The lock lifetime depends on the child process and exclusive file semantics.
