# File Research: sources/local-fs/xfsdump/common/content_inode.h

Purpose: defines the inode-style content strategy’s on-media structures, flags, and checksum helpers.

Key structures:
- `startpt_t`: identifies stream boundaries by inode, data-fork skip offset, and flags.
- `drange_t`: begin/end pair of `startpt_t`.
- `content_inode_hdr_t`: strategy-specific media-file header stored in `content_hdr.ch_specific`.
- `timestruct_t`: fixed on-media time representation independent of platform `timestruc_t`.
- `bstat_t`: fixed on-media bulk-stat representation independent of `xfs_bstat`.
- `filehdr_t`: fixed-size per-file header.
- `extenthdr_t`: per-extent header for file data, holes, alignment, or terminator.
- `direnthdr_t` and `direnthdr_v1_t`: current and older directory-entry media formats.
- `extattrhdr_t`: extended-attribute record header.

Key flags/constants:
- Startpoint flags: `STARTPT_FLAGS_END`, `STARTPT_FLAGS_NULL`.
- Media-file types: data, inventory, index.
- Dump attributes: subtree, index, inventory, incremental, retry, resume, inomap, dir dump, header checksums, dirent generation, extattr, not-self-contained.
- File header flags: null, checksum, end, extattr.
- Extent types: last, align, data, hole.
- Extended attribute flags: root, null, old checksum, secure, checksum.
- Alignment constants for dirents, symlinks, and xattrs.

Key helpers:
- `bstat_projid` reconstructs 32-bit project id from high/low 16-bit fields.
- `calc_checksum` returns a two’s-complement checksum over uint32_t words.
- `is_checksum_valid` checks whether a uint32_t-word checksum sums to zero.

Interactions:
- `arch_xlate.c` translates these structures for media compatibility.
- `drive_minrmt.c` writes and validates `content_inode_hdr_t` as part of media headers.
- Restore logic uses flags such as `POST_DATA_XFLAGS` to defer immutable/append/sync flag restoration until after data writes.

Risks/notes:
- All layout sizes are part of the dump format; comments record byte offsets and accumulated sizes.
- The checksum helpers require lengths divisible by `sizeof(uint32_t)` and assert this invariant.
