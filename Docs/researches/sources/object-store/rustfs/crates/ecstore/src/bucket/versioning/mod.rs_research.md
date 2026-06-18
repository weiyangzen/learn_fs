# sources/object-store/rustfs/crates/ecstore/src/bucket/versioning/mod.rs

## Purpose
This module adds behavior methods to the S3 `VersioningConfiguration` DTO, including whole-bucket status and prefix-specific enable/suspend decisions with RustFS excluded-prefix and folder-exclusion support.

## Important APIs, Types, and Functions
- `VersioningApi` defines `enabled`, `prefix_enabled`, `prefix_suspended`, `versioned`, and `suspended`.
- `enabled` and `suspended` compare `status` to S3 `Enabled` or `Suspended`.
- `prefix_enabled` requires bucket status enabled, allows empty prefix, rejects folder markers when `exclude_folders` is true, and rejects prefixes matching any configured excluded prefix pattern.
- `prefix_suspended` treats globally suspended buckets as suspended and also treats excluded folders/prefixes under enabled buckets as prefix-suspended.
- `versioned` is true when a prefix is either enabled or suspended.

## Control Flow and State Behavior
The code is pure DTO interpretation. Excluded prefixes are expanded into simple wildcard patterns (`sprefix*`) and matched with `rustfs_utils::string::match_simple`.

## Dependencies and Integration Points
It depends on `s3s::dto::{BucketVersioningStatus, VersioningConfiguration}` and RustFS wildcard matching. `versioning_sys.rs` uses this trait after reading bucket metadata.

## Persistence
No persistence in this file. It interprets persisted versioning configuration loaded elsewhere.

## Risks and Edge Cases
`prefix_enabled("")` returns true for any enabled bucket before checking exclusions, so root/list operations behave differently from concrete object prefixes. `versioned` returning true for suspended prefixes is semantically important because suspended buckets may still need null-version behavior. No inline validation exists for malformed excluded prefixes.

## Test Signals
No inline tests. Tests should cover enabled/suspended/absent statuses, folder exclusions, wildcard excluded prefixes, and the distinction between empty prefix and object prefix.
