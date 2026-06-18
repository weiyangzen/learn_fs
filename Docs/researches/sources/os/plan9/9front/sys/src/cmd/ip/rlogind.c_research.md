# File Research: sources/os/plan9/9front/sys/src/cmd/ip/rlogind.c

This is a minimal rlogin compatibility wrapper. It reads the initial rlogin strings from fd 0: an ignored error/port string, remote user, local user, and terminal type. It writes a NUL byte acknowledgement.

If the local user string is empty, it falls back to the remote user. It logs the selected user under syslog facility name `telnet` and execs `/bin/ip/telnetd -n -u <user>`.

`getstr` reads NUL-terminated fields byte by byte with a fixed output length, tolerating zero-length reads by continuing.
