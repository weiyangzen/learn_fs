# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/dirhash.h

This header defines the in-memory UFS directory hash accelerator.

Key contents:
- Defines empty/deleted slot markers for open-addressed hash tables.
- Defines hash scoring constants used for recycling.
- Defines two-level hash array layout constants.
- Defines `struct dirhash`, containing hash slots, per-directory-block free-space summaries, sequential lookup optimization state, score, and global list linkage.
- Declares build, lookup, add/remove/move, truncation, checking, init, and teardown functions.

Role:
- Speeds up large-directory lookup and free-space discovery while allowing memory-pressure recycling.
