# sources/object-store/rustfs/crates/kms/src/cache.rs

## Purpose
`cache.rs` provides a simple async metadata cache for KMS key metadata using `moka`. It is intended to improve repeated key metadata lookup performance.

## Important APIs, Types, and Functions
`KmsCache` wraps `Cache<String, KeyMetadata>`. Public methods are `new`, `get_key_metadata`, `put_key_metadata`, `remove_key_metadata`, `clear`, and `stats`. Test-only helpers include custom TTL construction, cache info, and contains-key checks.

## Control Flow
`new` constructs a cache with max capacity and fixed 5-minute TTL. `get_key_metadata` awaits a cache lookup. `put_key_metadata` inserts cloned metadata and runs pending tasks. `remove_key_metadata` removes a key. `clear` invalidates all entries and runs pending tasks. `stats` returns current entry count and a hard-coded zero miss count.

## State and Persistence Behavior
All cache state is in-memory and TTL-bound. It stores metadata only, not key material. Data is lost on process restart and invalidated by capacity/TTL policies.

## Dependencies and Integration Points
The cache depends on `moka::future::Cache`, `std::time::Duration`, and `crate::types::KeyMetadata`. Service layers can use it alongside backend metadata calls.

## Risks and Edge Cases
`put_key_metadata`, `remove_key_metadata`, and `clear` take `&mut self`, which limits sharing behind immutable `Arc` without external locking even though moka caches are internally concurrent. `stats` labels the second value as misses but always returns zero because moka's miss count is not exposed. TTL is fixed in `new` rather than accepting `CacheConfig` values; test-only helper supports custom TTL but production API does not.

## Test Signals
Unit tests verify put/get/clear behavior, TTL expiry with a short test TTL, and contains-key helper behavior. They do not test capacity eviction or concurrent access.
