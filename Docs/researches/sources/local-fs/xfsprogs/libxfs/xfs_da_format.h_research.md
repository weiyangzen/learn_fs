# File Research: sources/local-fs/xfsprogs/libxfs/xfs_da_format.h

## Purpose

`xfs_da_format.h` defines the shared on-disk formats for XFS directory/attribute blocks, da B-tree nodes, directory data/leaf/free blocks, attribute leaves, remote attributes, and parent pointer records.

## Key Contents

The header defines legacy and CRC-enabled magic numbers for da nodes, attr leaves, directory leaf blocks, directory data/block/free blocks, and remote attr blocks. `xfs_da_blkinfo` and `xfs_da3_blkinfo` provide common sibling-link and metadata-verification headers used by da nodes, attr leaves, and dir leaves.

For da nodes, it defines legacy/v3 node headers, node entries, flexible-array node blocks, maximum tree depth, and CRC offset. For directories, it defines shortform directory headers and entries, inode-number size rules, data block alignment, data/free entry structures, v2/v3 data headers, directory leaf headers/entries/tails, free-space blocks, and single-block directory tails and embedded leaf entry accessors.

For attributes, it defines shortform attr headers/entries, attr leaf headers, leaf entry records, local and remote name/value records, v3 attr leaf headers, namespace and state flags, on-disk masks, and entry-size helpers that preserve historical flexible-array padding semantics. It also defines remote attr block headers and the parent pointer record containing parent inode and generation.

## Dependencies and Risks

This header is the ABI for on-disk metadata. Risks are mostly layout-related: changing structure size, alignment, magic values, padding assumptions, or entry-size formulas would break compatibility. The attr entry-size helpers deliberately encode historical padding behavior, and the v3 structures rely on common leading fields so generic da code can manipulate sibling links safely across v2/v3 formats.
