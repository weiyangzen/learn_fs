# File Research: sources/os/plan9/9front/sys/src/cmd/srv.c

`srv.c` implements the Plan 9 `srv` command: connect to a 9P service by dialing a network address or running a command, post the connection in `/srv`, and optionally mount it.

Key functions:
- `usage` documents `srv [-abcCmnNq] [net!]host [srvname [mtpt]]` and `srv -e ...`.
- `ignore` handles alarm timeout and closed-pipe notes.
- `connectcmd` forks `/bin/rc -c cmd` with a pipe connected to stdin/stdout.
- `main` parses mount flags, auth options, command execution, retry/sleep options, derives `/srv/name` and `/n/name`, dials `netmkaddr(..., "9fs")` or runs a command, posts the fd, and mounts via `mount` or `amount`.
- `post` creates the service file and writes the connected fd number.
- `error` reports contextual failures.

Behavior:
- Supports `-a`, `-b`, `-c`, `-C`, `-m`, `-q` mount variations.
- `-n` disables authentication; `-N` also becomes user `none` before mounting.
- Retries once if mount fails with hangup/timeout after removing the srv file.

Risks:
- Command mode trusts the supplied shell command.
- Derived `/srv` and mount names depend on string parsing of host paths and `!`.
- `post` writes the fd but does not close the created srv file before exit; process exit handles cleanup.
