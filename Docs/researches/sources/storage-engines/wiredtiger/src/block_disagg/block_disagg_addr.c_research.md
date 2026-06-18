# sources/storage-engines/wiredtiger/src/block_disagg/block_disagg_addr.c

## Purpose

`block_disagg_addr.c` packs, unpacks, validates, formats, and checkpoint-wraps disaggregated-storage address cookies. It defines version compatibility behavior, optional debug upgrade/downgrade fields, supported flag masking, compact LSN/base-LSN encoding, and root checkpoint cookie serialization.

## Important APIs, Types, and Functions

Main functions are `__wti_block_disagg_addr_pack`, `__wt_block_disagg_addr_unpack`, `__wti_block_disagg_addr_invalid`, `__wti_block_disagg_addr_string`, `__wti_block_disagg_ckpt_pack`, and `__wti_block_disagg_ckpt_unpack`. Private helpers are `__block_disagg_addr_debug_upgrade`, `__block_disagg_addr_pack_version`, and `__block_disagg_addr_unpack_version`. The core type is `WT_BLOCK_DISAGG_ADDRESS_COOKIE` with `page_id`, `flags`, `lsn`, `base_lsn`, `size`, and `checksum`.

## Control Flow

Packing asserts a valid page ID and positive size, masks flags to `WT_BLOCK_DISAGG_ADDR_ALL_FLAGS`, optionally adds a debug optional flag, stores `base_lsn` as `lsn - base_lsn`, writes version/min-version, variable-length fields, fixed 32-bit checksum, and optional debug fields.

Unpacking computes the current readable version with debug settings, reads version/min-version, rejects cookies whose minimum version is newer than the reader, unpacks fields and checksum, validates debug fields when present, reconstructs `base_lsn`, rejects underflow, invalid page IDs, and zero size, returns only supported flags, and enforces exact cookie-size matching only for supported versions with no unsupported flags or optional debug field.

Checkpoint pack/unpack simply serialize or deserialize the root page's disaggregated address cookie into metadata checkpoint bytes.

## State and Persistence Behavior

Address cookies are durable metadata references to disaggregated page images and deltas. The format stores page identity, flags, LSN, base LSN delta, total size, and checksum. Debug knobs can intentionally write compatible or incompatible future-looking cookies to test upgrade behavior.

## Dependencies and Integration Points

This file is used by disaggregated read, write, checkpoint, and address-string methods. It depends on WiredTiger variable-length integer packing, fixed integer packing, connection debug settings, flag macros, and `WT_BM` address APIs. `block_cache/block_io.c` consumes disaggregated flags and sizes during multi-read delta handling.

## Risks and Edge Cases

Version compatibility is subtle: unsupported optional flags permit forward-compatible parsing only when size checks are relaxed. `lsn` must be greater than `base_lsn` during pack and not underflow during unpack. Returning only supported flags hides unknown flags from older readers by design. Debug optional fields alter size-check behavior and must not leak into production assumptions.

## Test Signals

Tests should cover normal pack/unpack round trips, compatible version bump, incompatible minimum-version rejection, optional-field parsing, unsupported flags with relaxed size checks, size mismatch errors, invalid page ID, zero size, LSN/base-LSN underflow, printable address strings, and checkpoint root cookie pack/unpack.
