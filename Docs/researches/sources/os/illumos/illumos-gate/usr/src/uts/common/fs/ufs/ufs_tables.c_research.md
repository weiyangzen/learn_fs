# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/ufs_tables.c

## Overview
`ufs_tables.c` defines static lookup tables used by UFS fragment allocation and accounting code. These tables encode bit patterns that help identify available fragments inside a filesystem block map.

## Main Responsibilities
- Provide `around[]` and `inside[]` masks used by `fragacct()` to detect fragment runs.
- Provide `fragtbl124[]` for fragment sizes 1, 2, and 4.
- Provide `fragtbl8[]` for fragment size 8.
- Export `fragtbl[MAXFRAG + 1]` to select the right fragment table by `fs_frag`.

## Data Semantics
- `around` and `inside` are used as pattern masks for expressions like `(map & around[size]) == inside[size]`.
- `fragtbl` maps a block bitmap pattern to bits indicating which fragment sizes are available.
- Entries for unsupported fragment counts are NULL.
- The comments preserve the original BSD/VAX `scanc` optimization context, but modern callers use the tables directly from C.

## Dependencies
- Consumed by `fragacct()` and UFS allocation logic that reasons about free fragments inside a block.
- Depends only on UFS constants such as `MAXFRAG` and the `uchar_t` type.

## Research Notes
This file is pure data. Any behavioral change here would affect low-level free-fragment accounting and allocation decisions across UFS.
