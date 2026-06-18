# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/common/libsys.c

- Role: Plan 9 system abstraction layer for upas mail tools.
- Major areas: Date/user lookup, mailbox lock-file management, file open/create/close wrappers, directory/stat helpers, system/domain names, process killing, pipe-note handling, console hold, mailbox path construction, user display-name lookup, remote address discovery, and mailbox creation.
- Locking: `syslock` waits for directory lock file; `trylock` creates/opens lock and forks a refresher; `sysunlock` closes and kills refresher.
- Mailbox helpers: `mboxpath`, `mboxname`, `deadletter`, `readlock`, and `creatembox` implement upas path policy.
- Risks/notes: Some lock failures are logged but treated as live-without-lock cases. `sysopenlocked` has exclusive open disabled “until system call is fixed.”
