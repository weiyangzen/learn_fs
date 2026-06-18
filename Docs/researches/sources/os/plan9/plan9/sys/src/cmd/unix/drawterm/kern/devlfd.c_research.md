# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devlfd.c

Wraps an existing host file descriptor as a Plan 9 `Chan` under device `#L`.

Key behavior:
- `lfdchan` creates a new channel whose `aux` holds the host fd.
- `lfdfd` installs such a channel into the Plan 9 fd table.
- Attach, walk, stat, and open are invalid and return `Egreg`.
- Close closes the underlying host fd.
- Read and write call host `read`/`write`; offsets are ignored because descriptors may be pipes.

Role:
- Provides a bridge for host descriptors used by drawterm internals, mount channels, or exports.

Notable risks:
- Always sets channel mode to `ORDWR`.
- Has no stat metadata and no seek support.
