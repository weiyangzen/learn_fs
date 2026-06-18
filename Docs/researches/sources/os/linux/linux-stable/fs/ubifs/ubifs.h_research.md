# File Research: sources/os/linux/linux-stable/fs/ubifs/ubifs.h

## Summary
Central private UBIFS header. It defines in-memory state, synchronization contracts, budgeting structures, journal/TNC/LPT/GC/orphan state, authentication helpers, and cross-file function prototypes for the UBIFS implementation.

## Main Responsibilities
- Defines UBIFS implementation constants, limits, journal head aliases, sequence/inode watermarks, shrinker ages, bulk-read limits, and debug/assert actions.
- Defines in-memory forms for keys, scanned nodes/LEBs, UBIFS inodes, write buffers, buds, journal heads, TNC znodes/branches, LPT nodes, lprops, budgeting, mount options, orphans, and per-superblock `struct ubifs_info`.
- Documents major locks and ownership rules, especially inode `ui_mutex`, xattr `xattr_sem`, write-buffer locks, commit locks, TNC mutex, LPT mutex, lprops lock, orphan lock, and budget/space locks.
- Provides authentication/hash/HMAC inline wrappers that compile to no-ops when authentication is disabled.
- Declares UBIFS APIs implemented across `io.c`, `scan.c`, `log.c`, `journal.c`, `budget.c`, `find.c`, `tnc.c`, `tnc_misc.c`, `tnc_commit.c`, `shrinker.c`, `commit.c`, `master.c`, `sb.c`, `replay.c`, `gc.c`, `orphan.c`, `lpt.c`, `lpt_commit.c`, `lprops.c`, `file.c`, `dir.c`, `xattr.c`, `super.c`, `recovery.c`, `ioctl.c`, `compressor.c`, `sysfs.c`, and `crypto.c`.

## Important Structures
- `struct ubifs_inode`: VFS inode extension with UBIFS dirty state, xattr accounting, bulk-read state, shadow size, compression flags, inline data, and optional fscrypt info.
- `struct ubifs_info`: per-mount superblock state covering UBI geometry, log/journal, commit state, TNC, master node, bulk-read buffer, area layout, key/hash settings, lprops/LPT, reserved pool, authentication, recovery, GC, background thread, sysfs stats, and mount options.
- `struct ubifs_budget_req` and `struct ubifs_budg_info`: operation budgeting and global budget accounting.
- `struct ubifs_znode` / `struct ubifs_zbranch`: in-memory TNC nodes and references, with optional authenticated hashes.
- `struct ubifs_lprops`, `struct ubifs_pnode`, `struct ubifs_nnode`: in-memory LEB property and LPT representation.
- `struct ubifs_wbuf`, `struct ubifs_bud`, `struct ubifs_jhead`: journal write-buffer and bud management state.

## Important Behavior
UBIFS uses its own inode dirty flag and `ui_mutex` because VFS can mark inodes dirty without giving UBIFS a chance to reserve flash space. The header documents that budgeted operations must control clean-to-dirty transitions.

Authentication wrappers centralize hash/HMAC no-op behavior, so callers can invoke helpers unconditionally while only authenticated mounts perform crypto work.

`struct ubifs_info` is a large cross-module contract. Many fields are protected by specific locks named in the comments; violating these lock domains can corrupt journal, lprops, TNC, or orphan state.

## Risks
This file has high blast radius. Changes to struct fields, flags, or helper semantics affect nearly every UBIFS source file. The most sensitive areas are inode dirty/budget locking, authenticated hash sizes, journal head state, LPT/lprops categorization, and recovery/mount-only fields.
