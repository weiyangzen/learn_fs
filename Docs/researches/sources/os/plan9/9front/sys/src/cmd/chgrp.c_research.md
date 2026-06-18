# File Research: sources/os/plan9/9front/sys/src/cmd/chgrp.c

Plan 9 `chgrp` command implementation.

Key behavior:
- Parses `-u` or `-o` to change owner/user instead of group.
- Requires a group/user argument followed by one or more files.
- For each file, builds a partial `Dir` with either `uid` or `gid` set and calls `dirwstat`.
- Reports per-file failures and exits with a non-nil status if any update fails.

Dependencies:
- Includes Plan 9 `<u.h>` and `<libc.h>`.

Research notes:
- Uses Plan 9 `Dir`/`wstat` semantics rather than POSIX `chown`.
