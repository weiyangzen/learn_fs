# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_inode_buf.c

## Role
`xfs_inode_buf.c` handles disk inode buffer verification, conversion between on-disk dinodes and in-core `xfs_inode` state, dinode CRC calculation, and validation of inode core fields, fork formats, extent-count encodings, metadata inode rules, and extent size hints.

## Main Responsibilities
- Verify inode cluster buffers for magic, inode version, and valid unlinked-list pointers.
- Map an inode location to its containing buffer with `xfs_imap_to_bp`.
- Decode and encode legacy and bigtime timestamps.
- Convert dinodes into in-core inode fields via `xfs_inode_from_disk`.
- Convert in-core inode fields back to dinode fields via `xfs_inode_to_disk`.
- Verify full dinode consistency with `xfs_dinode_verify`.
- Validate fork formats, fork offsets, large extent counter encoding, metadata inode constraints, extent size hints, and CoW extent size hints.
- Calculate v3 inode CRCs.

## Important Functions
- `xfs_inode_buf_verify` checks every inode in a buffer. Readahead verification suppresses normal corruption reporting and marks the buffer for reread with `-EIO`.
- `xfs_inode_from_disk` validates the dinode first, imports ownership, mode, timestamps, sizes, extents, flags, project id, v3 fields, forks, and initializes CoW/metadir accounting as needed.
- `xfs_inode_to_disk` writes in-core inode state into a dinode, including v2/v3 selection, metadata type, timestamps, fork formats, extent counters, UUID, inode number, and LSN.
- `xfs_dinode_verify_fork` validates local/extents/btree/meta-btree fork format rules and feature dependencies.
- `xfs_dinode_verify_forkoff` checks attr fork split points and special device fork offsets.
- `xfs_dinode_verify_metadir` enforces metadata inode constraints: v3 inode, metadata feature, valid metatype, zero permissions, root uid/gid, no DMAPI fields, mandatory flags, no DAX.
- `xfs_dinode_verify` performs the central dinode verifier, including CRC/UUID/ino checks, mode/type checks, extent count versus block count, realtime/reflink/bigtime feature checks, fork checks, and metadata inode checks.
- `xfs_inode_validate_extsize` and `xfs_inode_validate_cowextsize` validate hint flags, mode applicability, nonzero rules, alignment, max extent length, and AG-size bounds.

## Data and Invariants
- v3 dinodes must match filesystem UUID and inode number and pass CRC verification.
- v1 inodes are converted to v2-style in-core state; v1 `di_metatype` historically held old link count data.
- Large extent counters require the filesystem feature and zero padding in the alternate union field.
- Local directories must be local format when size fits in the inode; oversized data cannot claim local format.
- Metadata inodes using `XFS_DIFLAG2_METADATA` are deliberately hidden from userspace through mode and flag constraints.
- Metadata btree inodes have zero normal extent counts because their data fork is an embedded metadata btree root, not normal bmap extents.

## Error Handling and Corruption Response
- Verification failures return fail addresses to callers; import paths convert them to `-EFSCORRUPTED`, emit verifier errors, and mark inode/AG health sick.
- Buffer read failures that indicate sick metadata mark AG inode health sick in `xfs_imap_to_bp`.
- Hint validators intentionally retain historical compatibility around directory realtime hint alignment and expect callers to sanitize inheritance into regular files.

## Dependencies
This file integrates inode fork import from `xfs_inode_fork.c`, directory/attr validation, health reporting, metadata file flags, quota-independent metadata inode handling, and mount feature predicates.

## Research Notes
This is the main trust boundary for disk inode cores. Most later inode and fork code assumes the invariants enforced here: valid fork formats, valid v3 integrity fields, sane extent counters, and feature-compatible inode flags.
