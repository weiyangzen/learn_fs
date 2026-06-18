# File Research: sources/os/plan9/plan9/sys/src/cmd/srv.c

Plan 9 command for dialing or executing a service, posting it in `/srv`, and optionally mounting it.

Key responsibilities:
- Dials `net!host` service `9fs` or runs a command via `-e`.
- Posts the connected fd into `/srv/name`.
- Optionally mounts it at a derived or explicit mount point using `mount` or authenticated `amount`.
- Handles retry on hangup/timed-out mount by removing stale `/srv` entry.

Options:
- Mount placement flags: `-a`, `-b`, `-c`, `-C`, `-m`.
- `-n`: skip authentication and use `mount`.
- `-q`: post/check but do not mount.
- `-s`: sleep after connection before posting.
- `-e`: execute command instead of dialing.

Important functions:
- `connectcmd`: pipe to `/bin/rc -c`.
- `post`: writes fd number to `/srv/...`.
- `main`: derives srv name and mount point, connects, posts, mounts.

Risks/quirks:
- `post` leaves posted fd lifetime tied to process/fd semantics.
- Uses a 10-second alarm for connection establishment.
- Existing srv files are removed when mount retry sees hangup-like errors.
