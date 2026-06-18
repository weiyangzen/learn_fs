# File Research: sources/os/plan9/9front/sys/src/cmd/upas/fs/rename.c

This file implements local mailbox rename/move operations, including cross-directory copy fallback.

Key behavior:
- Detects delivery mailboxes needing broader permissions.
- `rollup` creates missing parent directories with delivery-aware modes.
- Same-directory non-delivery or directory renames use `dirfwstat` name changes.
- Cross-directory operations copy files/directories recursively and then remove or truncate the source depending on `Rtrunc`.
- `localrename` wraps `rename` for a mailbox backend.

Integration and risks:
- Used by local mailbox backends and `mboxrename`.
- `copydir` uses `d->mode` inside a loop where `d` is the array base, likely intended as `d[i].mode`; that is a correctness risk for recursive directory copying.
