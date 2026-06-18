# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/agb_bitmap.h

## Purpose

Defines a type-safe bitmap wrapper for `xfs_agblock_t` ranges used by XFS scrub code.

## Main Type

- `struct xagb_bitmap`
  - wraps `struct xbitmap32`

## Inline Operations

- lifecycle:
  - `xagb_bitmap_init`
  - `xagb_bitmap_destroy`
- mutation:
  - `xagb_bitmap_set`
  - `xagb_bitmap_clear`
  - `xagb_bitmap_disunion`
- queries:
  - `xagb_bitmap_test`
  - `xagb_bitmap_hweight`
  - `xagb_bitmap_empty`
  - `xagb_bitmap_count_set_regions`
- iteration:
  - `xagb_bitmap_walk`

## Non-Inline API

- `xagb_bitmap_set_btblocks`
- `xagb_bitmap_set_btcur_path`

## Research Notes

This header keeps scrub code explicit about AG block number units while reusing the generic 32-bit bitmap implementation.
