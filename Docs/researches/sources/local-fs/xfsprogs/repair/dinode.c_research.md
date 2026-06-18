# File Research: sources/local-fs/xfsprogs/repair/dinode.c

## Role

`dinode.c` is the central inode verifier and repair engine for `xfs_repair`. It validates on-disk inode cores, data forks, attribute forks, block mappings, symlinks, directories, quota files, realtime metadata files, reflink metadata, and metadata-directory inodes. It is called by phase 3 for inode discovery and semantic checks, and by phase 4 for duplicate-block detection and final block-map accounting.

## Main Responsibilities

- Translate and validate bmbt extent records for data and attr forks.
- Maintain repair’s in-core block ownership map while scanning inode forks.
- Detect duplicate, metadata, free, CoW, and invalid block claims.
- Validate realtime extents and rtgroup-aware realtime block mappings.
- Validate special XFS metadata inodes: root, quota, realtime bitmap/summary, rtrmap, rtrefcount.
- Repair correctable inode-core fields and clear unrecoverably corrupt inodes.
- Attempt bmap rebuilds from rmap data before clearing bad data/attr forks.
- Validate symlink, quota, directory, and attribute contents through specialized helpers.
- Mark metadata-directory tree contents for later recreation.

## Key Types and State

- `enum xr_ino_type` classifies discovered inode intent: directory, realtime data, quota, regular data, symlink, device, fifo/socket, realtime bitmap/summary/rmap/refcount.
- Static translated strings cache fork and file type names to avoid gettext contention in parallel AG scans.
- `zap_metadata` marks metadata directory files whose contents should be discarded because phase 6 rebuilds the metadata directory tree.

## Inode Clearing

- `clear_dinode_attr` removes an attr fork by resetting attr extent counts, attr format, shortform attr header, and `di_forkoff`.
- `clear_dinode_core` zeros and reinitializes a dinode core with magic, version, generation, formats, v3 inode number, and UUID.
- `zero_dinode` clears core, unlinked pointer, and fork payload.
- `clear_dinode` additionally notifies realtime/rmap/refcount repair code when critical metadata inodes are cleared, so later checks avoid trusting now-invalid metadata.

## Extent and Block Mapping Validation

`process_bmbt_reclist_int` is the core extent scanner. For each extent record it:

- Decodes disk bmbt records to in-core `xfs_bmbt_irec`.
- Verifies file offset ordering.
- Rejects zero-length extents.
- Rejects unwritten extents in attr forks and non-regular files.
- Validates physical block ranges against data device, realtime device, or rtgroup geometry.
- Ensures file offsets do not exceed `XFS_MAX_FILEOFF`.
- Optionally populates a per-inode `blkmap` used later to read directories, symlinks, quotas, and metadata files.
- Checks repair’s global in-core block map for illegal ownership conflicts.
- Marks accepted blocks as `XR_E_INUSE`, `XR_E_METADATA`, or `XR_E_MULT`.
- Adds reverse-map records when rmap collection is active.

The public wrappers split behavior:

- `process_bmbt_reclist` validates and updates the block map.
- `scan_bmbt_reclist` validates against known duplicate extents without mutating the block map.

## Realtime Handling

Realtime support has two paths:

- Legacy realtime extents use the compact `rt_bmap` and `rt_lock`.
- Rtgroup-enabled filesystems use the same grouped bmap abstraction as data AGs, with `isrt=true`.

`process_rt_rec`, `check_rt_rec_state`, and `process_rt_rec_state` validate realtime block ranges, enforce realtime extent alignment semantics, detect duplicate realtime references, and account for reflink-capable realtime files.

## Metadata Btree Inodes

The file supports in-inode roots for realtime metadata btrees:

- `process_rtrmap` validates realtime reverse mapping btree metadata files.
- `process_rtrefc` validates realtime refcount btree metadata files.

Both require metadata inode flags, verify association with an rtgroup when applicable, validate root level and root size, check key ordering, and traverse child blocks through `scan_lbtree`. They deliberately skip duplicate-block reprocessing when the metadata btree will be rebuilt.

## Data Fork Processing

`process_inode_data_fork` validates the data fork according to `di_format`:

- `LOCAL`: checks fork-local size limits.
- `EXTENTS`: scans inline extents.
- `BTREE`: validates and traverses bmap btree roots and children.
- `META_BTREE`: dispatches to realtime rmap/refcount validators.
- `DEV`: accepted for device inodes.

If a data fork is corrupt and rmap data is usable, it attempts `rebuild_bmap`. If rebuild fails, it clears the whole inode unless running in no-modify mode.

## Attribute Fork Processing

`process_inode_attr_fork` validates attr format, attr extent count, attr btree/extents, and optional semantic attr contents via `process_attributes`. On corruption it attempts attr fork bmap rebuild, then clears only the attr fork if rebuild fails. This is intentionally less destructive than clearing the whole inode because the data fork may already have been accounted into the global block map.

## Core Inode Validation

`process_dinode_int` is the main state machine. It validates and repairs:

- CRC, magic, inode version, `di_next_unlinked`.
- v3 inode number and UUID.
- Negative sizes.
- Free/in-use consistency against the in-core inode map.
- Mode and fork format compatibility.
- `di_flags` and `di_flags2` feature constraints.
- Metadata-directory flags.
- Reflink, realtime, bigtime, nrext64, and CoW extent-size feature compatibility.
- Timestamp nanoseconds for legacy timestamps.
- Extent size and CoW extent size hints.
- Size rules for directories, symlinks, special files, quotas, and realtime metadata inodes.
- Attr fork offset constraints.
- Data and attr fork block/extent counts.
- Semantic contents for directories, symlinks, and quota files.

It returns whether the inode was corrupt, while separately reporting whether it should be considered used, whether it is a directory, and whether the disk buffer must be written.

## Semantic Content Checks

- Directories are delegated to `process_dir2`.
- Symlinks are checked for length, zero size, remote block readability, CRC/header validity, and embedded NUL characters.
- Quota files are scanned by dquot cluster, with CRC, UUID, type, and record verification; bad dquot records are repaired in place if modification is allowed.

## Public Entrypoints

- `process_dinode`: full processing and possible repair.
- `verify_dinode`: core-only verification, no modification.
- `verify_uncertain_dinode`: quiet verification for candidate inodes discovered through directory entries.
- `get_agino_buf`: reads an inode cluster buffer and returns a pointer to a specific dinode.

## Repair Model

This file is conservative: structural inconsistencies that could lead to unsafe interpretation normally clear the inode or fork. Recoverable counter/flag/timestamp errors are fixed in place. Bmap rebuild is attempted only when rmap information can plausibly reconstruct fork mappings.

## Interactions

- Calls `process_dir2` for directory data.
- Uses `blkmap` helpers from `bmap` to map inode file offsets to physical blocks.
- Updates `incore` block states and inode state bits.
- Calls rmap/refcount/realtime repair helpers when metadata is invalidated.
- Depends on `globals` for no-modify mode, quota inode state, root/metadir repair flags, and feature-upgrade state.
