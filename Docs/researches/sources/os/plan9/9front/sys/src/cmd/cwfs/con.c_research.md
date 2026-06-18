# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/con.c

Interactive console command framework for cwfs. It installs commands/flags, starts a console command loop, and provides administrative actions for filesystems, users, stats, checks, dumps, profiling, and maintenance.

Important behavior:
- `consserve()` initializes console session, selects `main`, loads users, prints version, optionally touches cw superblock, then starts command processing.
- Command registry is sorted and invoked by whitespace-splitting `cmd_exec()`.
- Commands include `allow`, `cfs`, `check`, `clean`, `clri`, `create`, `dump`, `fstat`, `halt`, `remove`, `sync`, `users`, `version`, `who`, `hangup`, `printconf`, and others.
- Flag registry controls global/channel tracing and auth behavior.
- `walkto()` uses console 9P wrapper calls to resolve paths.
- `number()` parses signed vlongs for command arguments.
