# File Research: sources/local-fs/xfsprogs/db/dir2.c

Purpose: defines `xfs_db` field metadata and helper callbacks for XFS directory v2/v3 block, data, leaf, free, and node formats.

Key behavior:
- Exposes root field descriptors `dir2_hfld` and `dir3_hfld`.
- Defines field tables for:
  - v2/v3 directory top-level views.
  - block tails.
  - data bestfree entries.
  - data headers and data entry/unused unions.
  - leaf entries, leaf headers, and leaf tails.
  - free block headers and bests arrays.
  - DA block info, node entries, and node headers.
  - v3 CRC block headers and DA3 block info.
- Count/offset callbacks inspect magic numbers to expose only the fields valid for the current directory block format.
- Data-union callbacks distinguish live directory entries from unused regions by checking `XFS_DIR2_DATA_FREE_TAG`, compute variable name lengths, tag positions, and entry sizes.
- Block/data callbacks iterate variable-sized entry streams up to the block leaf area or data block end.
- Leaf/free/node callbacks derive array counts from on-disk headers and handle separate v2 and v3 header layouts.
- `dir2_size` returns the current directory geometry block size.
- `xfs_dir3_set_crc` updates the correct CRC offset for v3 block/data/free/leaf/node directory buffers.
- `xfs_dir3_db_buf_ops` supplies a special read verifier that detects the actual directory buffer type by magic number, swaps to the matching libxfs verifier, and calls it. The write verifier rejects unknown directory buffer writes.

Interactions:
- Registered through `field.c` as `FLDT_DIR2`, `FLDT_DIR3`, and many subfield types.
- Used by print/field traversal, CRC manipulation, directory navigation, and check code.
- Depends on `mp->m_dir_geo` and libxfs directory layout helpers.

Risks/notes:
- Field visibility depends on reading plausible magic values from the current buffer; corrupt buffers may expose few or no fields.
- The generic v3 directory verifier is read-time dispatch only; unknown write types are rejected.
