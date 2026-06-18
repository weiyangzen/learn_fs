<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/encode.rs -->
# sources/object-store/garage/src/util/encode.rs

## Purpose
Serialization helpers for non-versioned MessagePack encoding and debug JSON rendering.

## Important APIs, types, and functions
`nonversioned_encode`, `nonversioned_decode`, and `debug_serialize` wrap `rmp-serde` and `serde_json`.

## Control flow
Encoding uses `rmp_serde::Serializer::with_struct_map` for stable struct-map representation. Decoding reads from a byte slice. Debug serialization pretty-prints JSON or returns the JSON serialization error as a string.

## State and persistence behavior
Used for data formats that do not need the migration marker chain in `migrate.rs`. Once persisted, struct-map field naming and serde compatibility become part of the on-disk/network contract.

## Dependencies and integration points
Depends on serde, rmp-serde, and serde_json. Complements the migration-aware `Migrate` trait.

## Risks and test signals
Non-versioned encoding is risky for long-lived disk state because schema changes have no migration marker. Tests should cover round-trips and field additions where defaults are expected.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/encode.rs -->
