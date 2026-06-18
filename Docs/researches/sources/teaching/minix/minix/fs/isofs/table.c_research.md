# File Research: sources/teaching/minix/minix/fs/isofs/table.c

This file defines the isofs fsdriver dispatch table.

Registered operations:
- Mount/unmount, lookup, putnode.
- Read, getdents, readlink.
- Stat, mountpoint, statvfs.
- LMFS driver, block read/write, and flush hooks.

Disabled operations:
- `fdr_peek` and `fdr_bpeek` are inside `#if 0` because of subpage block size concerns.
- No write/create/unlink/rename operations are registered, matching read-only ISO9660 behavior.

Role:
- Binds the isofs implementation to MINIX fsdriver.
