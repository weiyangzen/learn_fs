# sources/object-store/rustfs/crates/ecstore/src/config/storageclass.rs

## Purpose
This file implements erasure storage-class configuration: standard/RRS parity, capacity optimization mode, and inline shard thresholds. It converts KVS and environment overrides into runtime placement behavior.

## Important APIs, types, and functions
Important exports include S3 storage-class constants, internal keys (`standard`, `rrs`, `optimize`, `inline_block`), env var names, `default_parity_count`, `StorageClass`, `Config`, `lookup_config`, `parse_storage_class`, `validate_parity`, and `validate_parity_inner`. `Config` exposes `get_parity_for_sc`, `should_inline`, `inline_block`, and `capacity_optimized`.

## Control flow
`lookup_config` resolves standard parity from env, then KVS, then default drive-count parity. RRS parity resolves from env, then KVS `rrs`, then single-drive zero or default one. It validates parity limits and standard-vs-RRS ordering. Inline block reads only the environment and defaults to 128 KiB, warning above that size.

## State and persistence behavior
The file owns static defaults only. Runtime configs are installed globally by config initialization. Environment overrides affect runtime lookup but are not persisted back into config.

## Dependencies and integration points
It depends on ecstore errors, `KV/KVS`, `serde`, `bytesize`, environment variables, and tracing. Object layout code uses the resulting global storage-class config for parity and inline decisions.

## Risks and edge cases
`lookup_config` appears to ignore persisted KVS values for `optimize` and `inline_block`, despite defaults and config conversion preserving them. Zero parity is allowed, which is required for some setups but risky in larger clusters. Unknown storage classes fall back to standard parity once initialized.

## Test signals
Tests verify RRS uses the internal `rrs` key and ignores the legacy `REDUCED_REDUNDANCY` key. `com.rs` tests cover storageclass encode/decode. Env overrides, inline behavior, optimize KVS behavior, and parity failure cases lack direct tests.
