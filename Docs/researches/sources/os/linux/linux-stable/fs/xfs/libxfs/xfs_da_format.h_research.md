# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_da_format.h

## Role
`xfs_da_format.h` defines the on-disk format structures and constants for XFS directory/attribute btrees, directory data/leaf/free/block layouts, shortform directories, attribute leaves, remote attributes, and parent pointer records.

## DA Btree Format
- Defines v2 magic values for DA nodes, attr leaves, and dir leaf blocks, plus v3 CRC-enabled equivalents.
- `struct xfs_da_blkinfo` is the common first field for leaf and internal blocks, carrying same-level forward/back links and magic.
- `struct xfs_da3_blkinfo` adds CRC, block number, LSN, UUID, and owner fields for metadata-CRC filesystems.
- `struct xfs_da_node_hdr`, `struct xfs_da3_node_hdr`, `struct xfs_da_node_entry`, `struct xfs_da_intnode`, and `struct xfs_da3_intnode` define internal btree nodes and separator entries.

## Directory Format
- Documents the four directory formats: shortform, single block, multiple data blocks with one leaf/free index, and node/leaf btree form.
- Defines v2/v3 block, data, and free magic values.
- Defines directory file type values `XFS_DIR3_FT_*` and their trace string mapping.
- Defines directory address-space concepts: data, leaf, and free spaces separated by 32GB logical regions.
- Defines shortform headers and entries, including helpers for variable-size headers and stored offsets.
- Defines data-block headers, free extents, active entries, unused entries, leaf blocks, leaf entries, leaf tails, free blocks, and single-block directory tails.
- Provides helpers such as `xfs_dir2_sf_hdr_size`, `xfs_dir2_sf_firstentry`, `xfs_dir2_data_unused_tag_p`, `xfs_dir2_leaf_bests_p`, and `xfs_dir2_block_leaf_p`.

## Attribute Format
- Defines shortform xattr headers/entries, leaf free maps, leaf entries, local name/value records, remote name records, and CRC-enabled attr leaf variants.
- Attribute leaf entries are sorted by hash and store namespace/status flags.
- Defines namespace and storage flags including local, root, secure, parent, and incomplete bits.
- Provides accessors for v2/v3 attr leaf header size, leaf entry arrays, and local/remote name-value payloads.
- Defines precise local and remote attribute entry size calculations that preserve historical on-disk layout after flex-array conversions.

## Remote Attributes and Parent Pointers
- Defines the v3 remote attribute block header with magic, offset, bytes, CRC, UUID, owner, block number, and LSN.
- Declares `xfs_attr3_rmt_buf_space`.
- Defines `struct xfs_parent_rec`, the packed parent pointer value containing parent inode and generation.

## Invariants
- Many structures are variable length and must be traversed through helper accessors rather than direct array assumptions.
- v3 formats add verification metadata but preserve layout relationships used by v2/v3 shared code, especially the common `xfs_da_blkinfo` prefix.
- Directory data entries are 8-byte aligned; attr name/value payloads are 4-byte aligned.
- Some attr entry size formulas are explicitly part of the on-disk ABI and cannot be changed even if C struct padding differs across architectures.

## Research Notes
This header is the on-disk ABI reference for the rest of the group. Most implementation complexity in the C files follows directly from these layout constraints: variable-length entries, end-of-block leaf/tail placement, shared v2/v3 prefixes, and duplicate hash keys.
