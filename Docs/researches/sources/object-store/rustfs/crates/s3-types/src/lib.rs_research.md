<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/s3-types/src/lib.rs -->
# sources/object-store/rustfs/crates/s3-types/src/lib.rs

## Purpose
Provides the public API surface for the `rustfs-s3-types` crate by exposing the event-name module.

## Important APIs, types, and functions
- Declares `mod event_name`.
- Re-exports `EventName`, `ParseEventNameError`, and `event_schema_version`.

## Control flow
There is no runtime control flow. The module declaration compiles `event_name.rs`, and the `pub use` line makes selected symbols available to downstream crates.

## State and persistence behavior
No state or persistence is implemented here. Persistence contracts come from the re-exported event enum's serialized strings and masks.

## Dependencies and integration points
Integrates `event_name.rs` with consumers such as `rustfs-s3-ops` and any notification code importing `rustfs_s3_types`.

## Risks and edge cases
Only the explicitly re-exported items are public. New helper functions added to `event_name.rs` will remain private to the crate unless added here.

## Test signals
No local tests exist. The re-export is validated indirectly when downstream crates and the `event_name.rs` tests compile.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/s3-types/src/lib.rs -->
