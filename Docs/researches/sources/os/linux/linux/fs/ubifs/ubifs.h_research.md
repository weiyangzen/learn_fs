# File Research: sources/os/linux/linux/fs/ubifs/ubifs.h

## Purpose
Central UBIFS internal header. It defines in-memory state, locks, subsystem data structures, inline auth/encryption helpers, and function prototypes for the UBIFS implementation.

## Main Contents
- Global constants for VFS magic, write sizes, sequence/inode watermarks, journal head aliases, shrinker age thresholds, bulk-read limits, and authentication array sizing.
- Core in-memory structs:
  - `struct ubifs_inode`: UBIFS inode overlay with xattr accounting, dirty state, UI size shadowing, fscrypt info, and locking.
  - `struct ubifs_info`: per-superblock master object containing UBI geometry, journal/log state, TNC state, budgeting, LPT/lprops, orphan tracking, GC, recovery, auth, mount options, sysfs stats.
  - `struct ubifs_wbuf`, `ubifs_jhead`, `ubifs_bud`: journal/write-buffer state.
  - `struct ubifs_znode`, `ubifs_zbranch`: Tree Node Cache/index representation.
  - `struct ubifs_lprops`, `ubifs_pnode`, `ubifs_nnode`, `ubifs_lpt_heap`: LEB properties/LPT state.
  - `struct ubifs_budget_req`, `ubifs_budg_info`: reservation and space-budget accounting.
- Enums for commit state, znode/cnode dirty/COW flags, scan results, lprops categories, GC return codes, assert actions.
- Inline authentication helpers wrapping hash/HMAC operations only when authenticated mode is active.
- External declarations and prototypes for UBIFS subsystems: auth, I/O, scanning, log, journal, budget, find, TNC, commit, master, superblock, replay, GC, orphan, LPT, lprops, file, dir, xattr, recovery, ioctl, compressor, sysfs, crypto, logging.

## Important Design Points
- `struct ubifs_info` is the ownership map for the whole filesystem instance. It documents which locks protect which fields, especially journal/log locks, commit locks, TNC mutex, space lock, lprops mutex, orphan lock, write-buffer locks, and mount/recovery-only state.
- UBIFS keeps its own inode dirty state and `ui_size` shadow to coordinate budgeting and avoid VFS writeback races.
- Authentication is compiled conditionally but abstracted through inline helpers so most call sites can be no-op in unauthenticated configurations.
- The file acts as the internal API contract between many C files; changes here have wide blast radius.

## Cross-File Relationships
- Includes `ubifs-media.h`.
- `xattr.c` uses `ubifs_inode`, budget requests, xentry keys, journal APIs, xattr handlers, and xattr/accounting constants declared here.
- All UBIFS implementation files rely on prototypes and shared structures declared here.

## Risks / Review Notes
- Locking is central and non-trivial. Changes to fields in `ubifs_inode` or `ubifs_info` need audit against documented lock ownership.
- Bitfield widths in `ubifs_budget_req` intentionally differ under `UBIFS_DEBUG`; budget arithmetic changes should be checked for overflow behavior.
- Auth helper return semantics use `crypto_memneq()` directly in `ubifs_check_hash()` / `ubifs_check_hmac()`, returning nonzero on mismatch rather than a conventional negative errno.
- Header exposes many cross-subsystem internals; refactors need careful dependency management.
