# File Research: sources/virtualization/qemu/block/parallels-ext.c

## Purpose
Implements read-only support for the Parallels format extension cluster, specifically persistent dirty bitmap loading. It is part of the Parallels image format driver and is used when an image has `ext_off` set and is opened read-only.

## Main Entry Points
- `parallels_read_format_extension()` reads the extension cluster and calls `parallels_parse_format_extension()`.
- `parallels_parse_format_extension()` validates the extension magic and MD5 checksum, walks feature records, and dispatches supported feature types.
- `parallels_load_bitmap()` parses a dirty-bitmap feature record, creates a QEMU dirty bitmap, reads its L1 table, and loads bitmap contents.
- `parallels_load_bitmap_data()` deserializes bitmap data clusters into the created bitmap.

## Internal Mechanics
The extension begins with `ParallelsFormatExtensionHeader`, including a magic value and MD5 checksum over the rest of the cluster. It then contains feature records with `ParallelsFeatureHeader`. Supported features are an end marker and a dirty-bitmap feature. Feature flags must be zero.

Dirty bitmap metadata includes disk size in sectors, bitmap UUID, granularity, and L1 table size. L1 entries map serialized bitmap chunks: `0` means all-zero chunk, `1` means all-one chunk, and larger values are sector-numbered locations of bitmap data clusters in the image. Loaded bitmaps are marked read-only because extension write support is not implemented.

## Dependencies
Uses QEMU dirty bitmap serialization APIs, `qcrypto_hash_bytes()` for MD5 validation, UUID helpers, aligned block reads, and shared Parallels state from `parallels.h`.

## Filesystem/Block Relevance
This file bridges image-format metadata to QEMU's persistent dirty bitmap model. It matters for backup/incremental-copy workflows that consume Parallels image bitmaps.

## Risks and Notes
- Format extensions are unsupported in writable mode by the main driver; this reader asserts read-only bitmap handling.
- Unknown features, nonzero feature flags, checksum mismatches, and malformed L1 sizes fail parsing.
- On parsing failure, bitmaps already created from earlier feature records are released.
- Feature data advancement is 8-byte aligned inside the extension cluster.
