<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/object-capacity/src/types.rs -->
# sources/object-store/rustfs/crates/object-capacity/src/types.rs

## Purpose
Defines shared data structures for capacity scanning. It separates public API summaries from crate-internal scan result details.

## Important APIs, Types, and Functions
`CapacityDiskRef` is the caller-provided disk identity with `endpoint` and `drive_path`. `CapacityScanResult` is crate-private and carries `used_bytes`, `file_count`, `sampled_count`, `is_estimated`, `scan_duration`, and `had_partial_errors`. `with_partial_errors` marks an internal result after aggregation detects failures. `CapacityScanSummary` is the public equivalent used by external tooling. The `From<CapacityScanResult>` implementation maps all fields to the public type.

## Control Flow
No complex control flow exists. The file provides constructors through derived defaults and a single conversion path.

## State and Persistence
All structures are value types with no persistence. `CapacityDiskRef` derives `Hash` and equality traits, enabling use in sets/maps when needed.

## Dependencies and Integration
Only depends on `std::time::Duration`. `scan.rs` creates and converts these values, while `lib.rs` re-exports the public disk reference and summary types.

## Risks
`file_count` and `sampled_count` are `usize`, which is natural in Rust but can be platform-width dependent for serialized or FFI callers if added later. Public `CapacityScanSummary` exposes `Duration`, so JSON or stable wire formats would require another DTO.

## Test Signals
No direct tests are present, but scan tests validate field semantics such as exact byte counts, file counts, estimates, and partial error propagation.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/object-capacity/src/types.rs -->
