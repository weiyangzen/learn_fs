# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_format.h

## Role in the repository

`xfs_format.h` is the central XFS on-disk format header for general metadata objects. It defines the binary layout, magic values, feature bits, sizing constants, and address conversion macros for the superblock, allocation group headers, realtime metadata, dinodes, quotas, symlinks, and the common btree record formats used by libxfs and kernel XFS code.

Directory/attribute formats and log formats are intentionally kept in other headers, so this file is the shared format contract for most non-directory on-disk structures.

## Superblock and feature model

The file defines both the incore `struct xfs_sb` and on-disk `struct xfs_dsb`. The on-disk form uses fixed-endian fields and includes legacy fields plus v5 additions such as CRC, feature masks, metadata UUID, metadata directory root, realtime group geometry, internal realtime start, and zoned realtime reservations.

Feature handling is split across:
- legacy `sb_versionnum` bits;
- older `sb_features2` bits;
- v5 compat, read-only compat, incompat, and log-incompat masks.

The v5 feature masks cover modern features including FINOBT, RMAPBT, reflink, INOBT block counts, ftype, sparse inodes, metadata UUID, bigtime, needsrepair, 64-bit extent counters, exchange range, parent pointers, metadata directories, zoned realtime, and realtime-group LBA gaps. Inline helpers test or mutate these feature fields.

## Addressing and allocation group formats

The header defines filesystem block, basic block, byte, allocation group, and disk address conversion macros. These are used throughout XFS to translate between global filesystem blocks, AG-relative blocks, disk addresses, and inode-derived positions.

Allocation group metadata formats include:
- `struct xfs_agf`, tracking free-space btree roots, levels, free counts, longest extent, rmap/refcount roots, btree block usage, UUID, LSN, and CRC.
- `struct xfs_agi`, tracking inode btree roots, levels, inode counts, free inode counts, unlinked inode buckets, FINOBT roots, and INOBT/FINOBT block counters.
- `struct xfs_agfl`, the AG freelist header.

The file also defines AGF and AGI logging bitmasks used by transaction code to log precise field ranges.

## Realtime metadata

Realtime definitions include old and realtime-group raw word formats for bitmap and summary words, realtime group limits, the realtime superblock `struct xfs_rtsb`, and constants for realtime bitmap/summary buffer headers. Realtime groups introduce per-group metadata and big-endian on-disk words for newer formats.

## Timestamp and metadata inode formats

The timestamp section documents legacy signed 32-bit second timestamps and bigtime unsigned 64-bit nanosecond-era timestamps. Helpers convert between Unix seconds and bigtime seconds. Quota bigtime conversion helpers similarly trade precision for wider expiration ranges.

`enum xfs_metafile_type` defines on-disk metadata inode types such as metadata directories, quota files, realtime bitmap/summary, realtime rmap, and realtime refcount files.

## Dinode format

`struct xfs_dinode` defines the on-disk inode core, including mode, format, ownership, project id, extent counters, timestamps, size, block count, flags, unlinked list pointer, v3 CRC fields, changecount, LSN, flags2, CoW/RT metadata fields, creation time, inode number, and UUID.

Important related definitions include:
- inode core size helpers for v2 versus v3 inodes;
- data/attribute fork size and pointer macros;
- device-number accessors for special files;
- legacy `di_flags` and newer `di_flags2`;
- metadata inode constraints and metadata flag definitions;
- inode number decomposition and composition macros.

The file also defines maximum extent count constants for old and large extent counter formats.

## Btree record formats

The header defines on-disk records, keys, pointers, and magic values for:
- allocation btrees by block number and by length;
- inode allocation btree and free inode btree;
- reverse mapping btree;
- realtime reverse mapping btree;
- refcount btree and realtime refcount btree;
- bmap btree records and inode-rooted bmap roots;
- generic short and long btree block headers.

The inode allocation record has full and sparse encodings. Sparse inode records use a holemask, inode count, free count, and free bitmap to represent partially allocated inode chunks.

## Other on-disk objects

The file defines dquot records and blocks, quota timer limits, remote symlink headers and limits, ACL records, ACL sizing rules, and on-disk ACL xattr names.

## Important invariants

- On-disk structures are fixed ABI; field order, endian annotations, padding, and size comments matter.
- V5 CRC fields must be accessed only when the filesystem supports CRC metadata.
- Superblock summary counter fields must remain contiguous for transaction delta application.
- Sparse inode records use zero holemask bits for physically allocated inode regions.
- Inode and block conversion macros assume mount geometry fields have already been validated.
- `sizeof(struct xfs_btree_block)` must not be used as an actual disk header size; short/long and CRC/non-CRC macros determine the real header length.
