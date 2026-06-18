# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/remove.c

This file implements local mailbox/folder removal for `upas/fs`.

Key behavior:
- Reuses `dirskip` from mdir backend to recognize message files.
- `idiotcheck` permits removal of directories, lock files, index files when requested, message files, and mbox-looking files.
- `rm` recursively removes allowable children depending on `Rrecur`.
- `rmidx` removes `.idx` and, unless truncating, `.imp`.
- `localremove` deletes or truncates a mailbox path, removes sidecar indexes, and returns static error text on failure.

Integration and risks:
- Used as backend `Mailbox.remove` for local mdir and Plan 9 mbox.
- Shares suspicious `isindex` logic with filterkit `mbremove.c`.
