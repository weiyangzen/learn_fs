# File Research: sources/os/plan9/9front/sys/src/cmd/upas/imap4d/folder.c

This file provides mailbox-directory helpers, global mail locking, and mailbox-name encoding/decoding helpers for the IMAP daemon.

Key behavior:
- Maintains cached current directory and wraps create/stat/wstat/open/remove operations after `mychdir`.
- `mblock`, `mbunlock`, `mblockrefresh`, and `mblocked` manage the shared `L.mbox` lock.
- `impname` creates the `.imp` sidecar name for a mailbox.
- `mboxname` decodes IMAP modified UTF-7, cleans the name, validates it, and encodes it for filesystem use.
- `strmutf7` and `mutf7str` convert between UTF-8 strings and IMAP modified UTF-7 using parse-bin allocation.

Integration and risks:
- Uses parse-bin allocation heavily; returned names are tied to parser allocation lifetime.
- `impname` calls `encfs` into a buffer but formats `%s.imp` from the original `name`, which appears inconsistent with intended encoded output.
