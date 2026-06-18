# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/quota.c

Implements quota usage reporting for IMAP quota commands.

Key responsibilities:
- Runs `/bin/du -s <mboxdir>` through a pipe.
- Parses the first tab-separated field as storage usage.
- Returns usage as a `vlong` byte/block value to `imap4d.c` quota handlers.

Filesystem relevance:
- Reports mailbox-directory disk usage for IMAP `GETQUOTA`/`GETQUOTAROOT`.
- Quota limit is hardcoded by the caller as `256*1024`.

Notable quirks:
- Uses a child process instead of direct tree traversal.
- `openpipe()` duplicates stdout to the pipe and logs exec failure through `ilog()`.
