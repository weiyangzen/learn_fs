# File Research: sources/local-fs/btrfs-progs/check/mode-lowmem.h

## Scope

This header defines low-memory checker error-bit constants and declares the two lowmem check entry points.

## Public APIs And Constants

- Fs-tree error bits include root-dir errors, missing/mismatched dir items, inode refs, inode items, file extents, csums, link counts, nbytes/isize, orphan items, root refs, dir indexes, block-group accounting, inode flags, dir hash mismatch, bad inode mode, invalid generation, super bytes-used mismatch, duplicate filename, and unknown key.
- Low-level extent/backref error bits include missing/mismatched backrefs, unaligned bytes, missing/mismatched referencers, crossing stripe boundaries, item-size mismatch, unknown type, accounting mismatch, chunk type mismatch, and out-of-order inline backrefs.
- Declares `check_fs_roots_lowmem()` and `check_chunks_and_extents_lowmem()`.

## Dependencies And Role

- Used by `mode-lowmem.c` and callers that need aggregate lowmem error classification.

## Risks And Invariants

- Error bits are used both for reporting and repair dispatch; overlapping or misused bits can trigger the wrong repair path.
- `REFERENCER_MISMATCH` and `CROSSING_STRIPE_BOUNDARY` share the same bit value in different internal contexts, so interpretation depends on the checker path.
