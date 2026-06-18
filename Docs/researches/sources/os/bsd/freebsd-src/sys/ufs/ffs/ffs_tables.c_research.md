# File Research: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_tables.c

## Role

Defines static fragment allocation lookup tables used by FFS allocation accounting code.

## Main Responsibilities

- Provides bit masks for detecting contiguous fragment runs.
- Provides precomputed fragment availability tables for supported fragment layouts.
- Exposes `fragtbl[]` indexed by `fs->fs_frag`.

## Important Data

- `around[9]`: masks for identifying a run plus surrounding bits.
- `inside[9]`: expected bit patterns for an available fragment run within the `around` mask.
- `fragtbl124[256]`: fragment availability table for fragment counts 1, 2, and 4.
- `fragtbl8[256]`: fragment availability table for fragment count 8.
- `fragtbl[MAXFRAG + 1]`: dispatch table mapping fragment count to the correct lookup table.

## How It Is Used

`ffs_fragacct()` in `ffs_subr.c` uses these tables to update cylinder group fragment summary counts when fragments are allocated or freed.

For a given block bitmap byte pattern, the tables report whether a fragment of a particular size exists. This avoids recomputing contiguous-fragment availability from scratch for common bitmap patterns.

## Research Relevance

This file is small but important for understanding classic FFS fragment accounting. It captures the precomputed table-driven design used to make fragment allocation fast, especially in historical architectures where instructions such as VAX `scanc` could exploit compact lookup tables.
