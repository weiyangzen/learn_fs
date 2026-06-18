# File Research: sources/os/linux/linux/fs/xfs/scrub/agb_bitmap.h

## Purpose

`scrub/agb_bitmap.h` defines a type-safe bitmap wrapper for XFS allocation group block numbers and declares btree block marking helpers used by scrub code.

## Main Content

- Defines `struct xagb_bitmap` as a wrapper around `struct xbitmap32`.
- Provides inline wrappers for:
  - Initialize and destroy.
  - Clear and set ranges.
  - Test a range.
  - Subtract/disunion another bitmap.
  - Count set blocks.
  - Check emptiness.
  - Walk set regions.
  - Count set regions.
- Declares helpers to mark all btree blocks or the current btree cursor path.

## Key Interfaces and Invariants

- The wrapper provides type clarity for `xfs_agblock_t` ranges while reusing 32-bit sparse bitmap storage.
- Range lengths use `xfs_extlen_t`.
- Walk callbacks use the generic `xbitmap32_walk_fn` signature.
- Region counting delegates directly to `xbitmap32`.

## Dependencies

Depends on `xbitmap32`, XFS AG block and extent length scalar types, and generic btree cursor declarations from the scrub build context.
