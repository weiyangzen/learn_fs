# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/ddt_zap.c

## Role

`ddt_zap.c` provides the ZAP-backed persistent storage implementation for DDT entries. It implements the `ddt_ops_t` interface consumed by `ddt.c`.

## Major Responsibilities

- Creates and destroys DDT ZAP objects.
- Looks up, prefetches, updates, removes, walks, and counts DDT entries in a ZAP object.
- Stores DDT keys as uint64 ZAP keys and compressed DDT physical-entry arrays as values.

## Key Tunables

- `ddt_zap_leaf_blockshift = 12`
- `ddt_zap_indirect_blockshift = 12`

These control leaf and indirect block sizes for created DDT ZAP objects.

## Important Functions

- `ddt_zap_create()` creates a ZAP object with:
  - `ZAP_FLAG_HASH64`
  - `ZAP_FLAG_UINT64_KEY`
  - optional `ZAP_FLAG_PRE_HASHED_KEY` when the checksum supports dedup prehashing
  - object type `DMU_OT_DDT_ZAP`
- `ddt_zap_destroy()` destroys the ZAP object.
- `ddt_zap_lookup()` obtains the stored compressed value length, reads it, and decompresses it into `dde->dde_phys`.
- `ddt_zap_prefetch()` prefetches a DDT key using `zap_prefetch_uint64()`.
- `ddt_zap_update()` compresses `dde->dde_phys` with `ddt_compress()` and writes it with `zap_update_uint64()`.
- `ddt_zap_remove()` removes a DDT key.
- `ddt_zap_walk()` iterates with a serialized ZAP cursor, intentionally avoiding whole-object prefetch on the first cursor because DDT objects may be huge.
- `ddt_zap_count()` wraps `zap_count()`.

## Interactions

- Depends on `ddt_compress()` and `ddt_decompress()` from `ddt.c`.
- Uses uint64-key ZAP APIs so `ddt_key_t` words can be used directly as keys.
- Exports `const ddt_ops_t ddt_zap_ops`, which is registered in `ddt.c`.

## Notable Invariants

- The ZAP value is a compressed byte stream no larger than `sizeof (dde->dde_phys) + 1`.
- Lookup expects the ZAP value integer length to be one byte.
- Walk records the serialized cursor back into `*walk`, allowing resumable DDT traversal.
- On successful walk, the key is reconstructed from `za.za_name`.

## Research Notes

This file is intentionally narrow: it is persistence glue, not dedup policy. Any behavioral changes should be checked against `ddt.c` expectations for key layout, compressed payload format, walk cursor behavior, and no-prefetch iteration.
