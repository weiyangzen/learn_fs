# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/filesystem_driver/common.rs

## Purpose
Common non-benchmark helper for constructing deterministic `RequestInfo` used by in-process rustfs drivers.

## Important APIs, types, and functions
- `request_info()` returns `RequestInfo` with zeroed `unique`, uid, gid, and pid.

## Control flow
No branching; creates a value on demand.

## State and persistence behavior
No state. The fixed uid/gid/pid influence permission metadata in operation-count tests.

## Dependencies and integration points
Used by `fuse_mt.rs` and `fuser.rs` to invoke rustfs high-level/low-level APIs without a real kernel FUSE request.

## Risks and edge cases
All tests run as uid/gid zero from the filesystem API's perspective, so permission behavior may differ from mounted benchmark/syscall paths.

## Test signals
Indirectly covered by all in-process filesystem driver tests.
