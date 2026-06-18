# File Research: sources/local-fs/xfsprogs/libxfs/xfs_dir2.h

## Purpose

`xfs_dir2.h` declares the public directory interfaces, directory geometry helpers, format classifiers, buffer ops, conversion helpers, and inline offset/name utilities for XFS v2/v3 directories.

## Key Contents

The header exposes dot and dotdot names, same-name comparison, directory format enum, mode-to-filetype conversion, mount startup/teardown, high-level create/lookup/remove/replace/canenter APIs, `xfs_da_args` variants, shortform-to-block conversion, directory block shrink, data-block free-space helpers, inode validation, block/leaf/free/data buffer ops, and v3 header checks.

It provides inline conversions among directory byte offsets, dataptrs, logical directory blocks, and da blocks. It also defines tail and leaf-array accessors for block and leaf formats, the readdir buffer size estimate, filetype extraction, data end offset, and name validation.

ASCII-CI helpers fold selected ASCII/Latin-1 uppercase byte ranges for historical case-insensitive directory hashing. Optional live hook declarations allow directory update notification. The parent-pointer-aware `xfs_dir_update` APIs declare create/add/remove/exchange/rename child workflows.

## Dependencies and Risks

Most helpers assume geometry fields are already initialized and that offsets are aligned to directory data alignment. Incorrect conversion between dataptr, db, da, and byte offsets would corrupt directory metadata. Callers must also respect filetype feature availability, owner checks, and parent pointer argument lifetime.
