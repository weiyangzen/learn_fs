# File Research: sources/os/plan9/plan9/sys/src/cmd/tlssrv.c

TLS server wrapper that serves TLS on fd 1 and connects cleartext to stdin/stdout or a child command.

Key responsibilities:
- Parses certificate `-c`, debug `-D`, syslog name `-l`, and remote-system label `-r`.
- Reads a PEM certificate chain and passes it to `tlsServer`.
- Optionally traces libsec TLS messages through `reporter`.
- Optional `-D -D` style dumping can hex-dump traffic through a pipe wrapper.
- If a command is supplied, forks it with stdin/stdout connected to a pipe.
- Runs bidirectional cleartext-to-TLS copy loops and tears down the process group on EOF or error.

Notable risks:
- `xfer()` forks and returns in the child, with the parent doing copy work; this is subtle and easy to misread.
- `death()` repeatedly posts notes to the current process group and exits, so shutdown is intentionally broad.
- In no-command mode, cleartext fd 0 and TLS fd 1 assumptions are central to correct use.
