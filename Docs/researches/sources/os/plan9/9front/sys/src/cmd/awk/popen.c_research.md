# File Research: sources/os/plan9/9front/sys/src/cmd/awk/popen.c

Implements awk pipe open/close support on Plan 9.

Key responsibilities:
- Provides `popen` by creating a pipe, forking, and executing `/bin/rc -c cmd`.
- Tracks up to `MAXFORKS` active child processes with fd, pid, done flag, and status text.
- Closes inherited file descriptors in the child after duplicating the pipe end.
- Provides `pclose` to close the `Biobuf`, wait for the matching child, and return command status.

Important interfaces:
- Exports `Biobuf *popen(char*, int)` and `int pclose(Biobuf*)`.
- Used by awk runtime redirection/pipe execution.

Notes:
- `pclose` waits broadly and records statuses for other tracked children it reaps along the way.
- Status buffer copy uses `strecpy` with an apparent `+512` bound despite `status[128]`.
