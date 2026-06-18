# File Research: sources/local-fs/xfsprogs/db/check.c

Purpose: implements several `xfs_db` consistency and diagnostic commands centered on whole-filesystem block ownership, inode/link accounting, quota verification, directory verification, realtime metadata verification, block use reporting, and deliberate metadata fuzzing.

Commands registered by `check_init`:
- `blockget`: builds in-memory block/inode ownership maps and checks filesystem consistency.
- `blockfree`: frees the maps allocated by `blockget`.
- `blockuse`: prints recorded ownership/type for current disk block(s).
- `blocktrash`: expert-mode command to randomly or explicitly flip/set/clear/randomize bits in selected metadata blocks.
- `ncheck`: prints inode-to-path mappings after `blockget -n`.

Core data structures:
- `dbm_t` classifies every filesystem/realtime block as superblock, AGF/AGI/AGFL, free space btrees, inode btrees, data, directory, attr, quota, realtime bitmap/summary/data/free, reflink data, CoW staging data, etc.
- `dbmap` records block type per AG or realtime area.
- `inomap` records inode owner per block.
- `inodata_t` tracks per-inode link counts, directory parent/name data, selected inode filtering, security-sensitive inode marker, directory status, and reflink state.
- `blkmap_t` maps file logical block offsets to physical fsblocks for directory, quota, realtime bitmap, and realtime summary scans.
- `qdata_t` accumulates computed and on-disk quota block/inode/realtime counts by quota id.
- Directory leaf/data cross-checking uses a hash table of `(hashval,address)` entries to detect missing and extra leaf entries.

Key behavior:
- `init` validates the primary superblock and log state, allocates per-AG and optional realtime maps, initializes inode hash tables sized from `sb_icount`, parses `blockget` options, infers expected superblock feature bits, and initializes quota checking state.
- `scan_ag` reads each AG superblock, AGF, and AGI; marks fixed metadata blocks; scans the AGFL; scans bnobt/cntbt/rmapbt/refcountbt/inobt/finobt; compares counted free blocks, btree blocks, inode counts, and unlinked-list state against AG headers.
- Allocation btree scan functions mark and cross-check free-space records from bnobt and cntbt, detect out-of-order records, and update `fdblocks`, `agffreeblks`, and `agflongest`.
- Inode btree scan functions read inode chunks, handle sparse inode records, mark inode allocation blocks, process allocated/free dinodes, and compare free counts.
- `process_inode` validates dinode magic/version/format/fork layout, link state, unlinked state, nblocks/nextents/anextents, dispatches local/extents/btree forks, accounts quota usage, and invokes directory/realtime/quota special-file checkers.
- Bmap scanning handles local, extent, and btree forks, marks owned blocks, detects duplicate ownership, tracks per-file `blkmap_t` data, and supports reflink by allowing shared data/reflink-data transitions.
- Directory checking covers shortform, block, leaf, and node directory formats. It verifies `.`/`..`, parent consistency, data bestfree arrays, free-entry tags, leaf hash entries, stale counts, free index blocks, and v2/v3 magic variants.
- Realtime checking reads realtime bitmap and summary files, marks free realtime extents, computes summary counts from the bitmap, and copies on-disk summary data for comparison support.
- Quota checking reads checked quota files, validates quota record magic/version/type/id, and compares on-disk quota accounting against inode-derived counters.
- `ncheck` reconstructs paths from recorded directory parent/name links and can filter by inode or security-sensitive entries.
- `blocktrash` can choose eligible block classes from the `dbmap`, select random blocks by seed, or alter the current buffer with `-z`; it temporarily disables buffer write verification to write intentionally bad data.

Interactions:
- Relies on `libxfs` geometry, btree, directory, inode, realtime, and quota helpers.
- Uses `set_cur`, `push_cur`, `pop_cur`, `write_cur`, type descriptors, and current IO buffers from the `xfs_db` core.
- Uses `convert_extent`, `bmap`, `make_bbmap`, and type tables to walk and read mapped metadata.
- Shares field/type names with `type.c`, `field.c`, `dir2.c`, and `dquot.c`.
- `blocktrash` is only registered when `expert_mode` is enabled.

Risks/notes:
- This is a diagnostic checker, not a repair engine; several comments explicitly defer deeper refcount validation to `xfs_repair`.
- Many scans continue after nonfatal errors but set global `error`, `serious_error`, and `exitcode`; callers must interpret exit status carefully.
- `blocktrash` intentionally corrupts metadata and bypasses verifier protection for testing.
- The checker is tightly coupled to on-disk XFS format details and feature flags, including reflink, finobt, rmapbt, v5 CRC metadata, realtime devices, and sparse inodes.
