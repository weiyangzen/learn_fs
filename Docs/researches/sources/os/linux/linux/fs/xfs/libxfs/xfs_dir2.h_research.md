# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_dir2.h

## Scope

This header declares the public XFS directory interface, directory format enumeration, directory data/free logging helpers, buffer ops, address conversion helpers, block-tail accessors, ASCII case-insensitive helpers, optional live hook interfaces, and child update operation structures.

## Main Interfaces

- Exports `xfs_name_dot` and `xfs_name_dotdot`.
- `xfs_dir2_samename()` compares two `xfs_name` values.
- `enum xfs_dir2_fmt` identifies shortform, block, leaf, node, and error formats.
- Declares generic directory APIs: init, create, lookup, remove, replace, can-enter, and args-level variants.
- Declares direct shortform-to-block conversion and directory shrink helper.
- Declares data block free/logging helpers and data/free/leaf/block verifiers and buffer ops.
- Provides inline conversions among directory byte offsets, dataptrs, logical DB blocks, and DA blocks.
- Provides single-block tail and leaf-tail pointer helpers.
- Defines `XFS_READDIR_BUFSIZE`.
- Declares filetype and name validation helpers.
- Defines ASCII case-insensitive transform helpers for the historical `ascii-ci` feature.
- Defines live hook structures and child update structures/APIs.

## Data Model

Directory offsets use several related coordinate systems: file byte offsets, compact dataptrs, logical directory DB blocks, and DA blocks. The inline helpers centralize conversions using `xfs_da_geometry` so directory implementations can move between on-disk leaf addresses and buffer offsets safely.

## Dependencies

Includes `xfs_da_format.h` and `xfs_da_btree.h`, and is included by generic directory code, shortform/block/leaf/node implementations, readdir, parent pointer code, and userspace-oriented libxfs consumers.

## Risks And Invariants

- Conversion helpers depend on geometry fields initialized at mount time; incorrect `blklog` or `fsblog` corrupts address calculations.
- Tail accessors assume fixed placement at the end of the directory block.
- `ascii-ci` intentionally handles a limited byte transform and does not imply general Unicode casefolding.
- Hook declarations compile to no-ops without `CONFIG_XFS_LIVE_HOOKS`; callers must tolerate both builds.
