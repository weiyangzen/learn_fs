# File Research: sources/os/plan9/plan9/sys/src/cmd/lp/lpdaemon.c

Read fully: 448 lines, 9910 bytes. SHA-256 prefix: `9416d4299d9513e4`.

This is a portable LPD/lp receiver daemon. It reads requests from stdin, accepts BSD lpr-style control/data file transfers or simpler local lp protocol input, writes jobs to temporary files, extracts user/host from control files, constructs arguments, and forks the local `lp` command.

Key routines:
- `error()` appends timestamped logs.
- `forklp()` logs and executes `LP` with parsed args.
- `tempfile()` creates unlinked temporary files.
- `readline()` and `readfile()` implement line and counted-data protocol reads with ACK/NAK and alarms.
- `getfiles()` receives LPD control and data files.
- `getjobinfo()` parses `H` and `P` control-file records.
- `main()` parses first command byte and builds the lp argument vector for queue, receive, remove, or direct print paths.

Integration: conditional paths support Plan 9, V10, SYSV, and BSD host environments.

Risk notes: manual varargs logging is nonportable. Argument and line buffers are fixed. Protocol timeouts are alarm-based.
