# File Research: sources/local-fs/xfsprogs/libxfs/xfs_inode_buf.c

## Role

This file verifies inode buffers, maps inode locations to buffers, converts dinodes between on-disk and incore forms, calculates inode CRCs, and validates inode core metadata. It is the main libxfs bridge between raw `struct xfs_dinode` storage and `struct xfs_inode`.

## Inode Buffer Verification

`xfs_inode_buf_verify` checks every dinode in an inode buffer for:

- correct inode magic
- supported inode version
- valid `di_next_unlinked` AG inode pointer

Read verification reports corruption through the buffer verifier. Readahead verification treats invalid buffers as failed readahead by clearing `XBF_DONE` and setting `-EIO`, avoiding noisy recovery-time warnings.

Exports:

- `xfs_inode_buf_ops`
- `xfs_inode_buf_ra_ops`
- `xfs_imap_to_bp`

`xfs_imap_to_bp` reads the buffer containing a mapped inode and marks the AG inode metadata sick if metadata errors are detected.

## Disk To Incore Conversion

`xfs_inode_from_disk` validates the dinode with `xfs_dinode_verify`, loads permanent inode fields, and returns early for unused inodes. It handles:

- v1 inode link count compatibility
- uid/gid/project id
- legacy and bigtime timestamps
- size, blocks, extsize, fork offset, flags, unlinked pointer
- v3 fields including change count, creation time, flags2, CoW extent size, and large extent count union
- data fork and optional attr fork formatting
- CoW fork creation for reflink inodes
- metadata inode statistics adjustment

On attr fork formatting failure it destroys the already loaded data fork.

## Incore To Disk Conversion

`xfs_inode_to_disk` writes incore inode fields into a dinode, choosing v2 or v3 format from mount features. It writes the metatype only for metadata inodes, converts timestamps, stores fork formats, extent counters, flags, ids, link count, generation, device fields via fork flush, and v3 UUID/LSN/CRC-related fields.

`xfs_inode_to_disk_iext_counters` chooses normal or large extent counter fields and clears padding during upgrades.

`xfs_dinode_calc_crc` computes the v3 inode checksum over the full inode size.

## Dinode Validation

`xfs_dinode_verify` is the central inode verifier. It checks:

- magic, version, CRC, inode number, and metadata UUID
- metatype rules for v2/v3 and metadata inodes
- nonnegative file size
- mode-to-filetype validity
- zero-length symlink/directory rules for linked inodes
- large extent counter feature and padding
- extent counts versus block count
- directory max extents
- fork offset placement
- realtime flag availability
- data and attr fork formats
- extsize and cowextsize hints
- reflink feature and inode mode restrictions
- realtime/reflink compatibility
- bigtime feature compatibility
- metadata inode rules
- nonzero block counts with zero extents, except metadata btree forks

`xfs_dinode_verify_fork` validates local, extents, btree, and metadata-btree fork formats. Metadata btree forks are limited to supported metadir metafile types such as realtime rmap and realtime refcount metadata.

`xfs_dinode_verify_metadir` enforces metadata inode constraints: v3 only, valid metatype, directory or regular file only, zero permissions, zero uid/gid, no DMAPI state, mandatory immutable/sync/noatime/nodump/nodefrag flags, directory no-symlinks flag, and no DAX.

## Hint Validators

`xfs_inode_validate_extsize` validates data extent size hints for directories and regular files, including flag/mode compatibility, nonzero hints when flags are set, block or realtime extent alignment, max bmbt length, and AG half-size limits.

`xfs_inode_validate_cowextsize` validates CoW extent size hints similarly, requiring reflink support when the flag is set. Both validators preserve historic leniency around directory hints that may become realtime-alignment-invalid after adding a realtime device.

## Dependencies

This file coordinates with inode fork formatting, bmap extent validation, metadata health marking, transaction buffer reads, directory geometry, superblock feature predicates, metadir/metafile support, and timestamp conversion helpers.

## Research Notes

This file is the authoritative dinode policy gate. Changes to inode feature bits, fork formats, metadata inode types, timestamp encodings, or extent counters must be reflected here or filesystems may be incorrectly accepted, rejected, or written in a format older kernels cannot understand.
