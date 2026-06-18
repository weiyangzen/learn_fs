
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/integrity/integrity_data/serialization.rs

## Purpose
This file defines the binary representation of `KnownBlockVersions`. It maps the live lockable per-block state into deterministic serialized fields with a format header, prior-violation flag, known client/block versions, and last-update/deleted state per block.

## Important APIs, Types, and Functions
- `FORMAT_VERSION_HEADER` is `cryfs.integritydata.knownblockversions;1`.
- `KnownBlockVersionsSerialized` derives `BinRead`/`BinWrite` little-endian and contains:
  - `header: Vec<NonZeroU8>` parsed/written as a NUL-terminated string.
  - `integrity_violation_in_previous_run: bool`.
  - `known_block_versions: HashMap<(ClientId, BlockId), BlockVersion>`.
  - `last_update_client_id: HashMap<BlockId, MaybeClientId>`.
- `From<KnownBlockVersionsSerialized> for KnownBlockVersions` reconstructs `LockableHashMap<BlockId, BlockInfo>`.
- `KnownBlockVersionsSerialized::async_from(KnownBlockVersions)` consumes live state and flattens it into the two persisted maps.
- `format_potential_utf8()` improves wrong-header diagnostics for non-UTF-8 bytes.

## Control Flow
Deserialization first validates the exact header, then reads the violation bool and two hash maps. Reconstruction creates block entries from `last_update_client_id` first, then merges client-version entries, creating unknown `BlockInfo` entries if versions exist without a last-update row. Serialization waits until `Arc::strong_count(&data.block_infos) == 1`, then `Arc::into_inner()` consumes the lockable map and iterates entries into the two flat maps.

## State and Persistence Behavior
The serialized model intentionally separates "who last updated this block" from "what versions have we seen for each client". Deleted state is represented by `MaybeClientId::BlockWasDeleted` in the `last_update_client_id` map, encoded as zero by the type's binary implementation. Hash-map order is not stable, and tests accept both entry orders.

## Dependencies and Integration Points
The file relies on CryFS binary helpers for bool/hashmap/NUL-string parsing, `HashMapExt::try_insert()` for duplicate detection, and `lockable::LockableHashMap` for reconstructing live state. It is called by `KnownBlockVersions::load/save`.

## Risks and Edge Cases
- `async_from()` busy-waits with `tokio::task::yield_now()` until all outstanding block-info guards release their `Arc`. The comment notes a possible deadlock if a held guard depends on the current task.
- Duplicate keys in serialized maps panic via `expect`, so malformed duplicate input may abort rather than produce a recoverable error.
- Compatibility with the C++ version is marked as TODO.
- Header mismatch is detected cleanly, but unsupported future formats are hard failures.

## Test Signals
Tests cover wrong UTF-8 and non-UTF-8 headers, invalid booleans, empty/non-empty maps, combined map serialization, extra trailing bytes, and order-insensitive serialized hashmap variants.
