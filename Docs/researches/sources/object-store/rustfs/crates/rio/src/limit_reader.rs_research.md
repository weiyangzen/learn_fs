<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/limit_reader.rs -->
# sources/object-store/rustfs/crates/rio/src/limit_reader.rs

## Purpose
Implements a soft byte-limiting `AsyncRead` wrapper that stops after a configured number of bytes without treating extra bytes in the inner reader as an error.

## Important APIs, types, and functions
- `LimitReader<R>::new(inner, limit)` creates the wrapper.
- Fields track `limit`, `read`, and a `scratch` buffer for partial allowed reads.
- `AsyncRead::poll_read` enforces the visible byte cap.
- Capability delegation uses `delegate_reader_capabilities_generic!`.

## Control flow
Each read computes `remaining = limit - read`. If no bytes remain, it returns EOF. If the caller buffer has room for no more than the remaining limit, it polls the inner reader directly and increments `read` by the new bytes. If the caller buffer is larger than the allowed remainder, it polls the inner reader into `scratch`, copies only the filled bytes into the caller buffer, and updates `read`.

## State and persistence behavior
State is in-memory byte accounting plus a reusable scratch buffer. The wrapper does not consume or validate bytes after the limit, so the underlying stream may still contain data. This is suitable for range-like truncation, not strict content-length enforcement.

## Dependencies and integration points
Depends on Tokio `AsyncRead` and `pin_project_lite`. It integrates with the same reader capability system as other wrappers, allowing ETag and hash metadata discovery through the limit layer.

## Risks and edge cases
Because extra bytes are not rejected, using `LimitReader` for client-declared content length would allow overlong bodies to be accepted by callers that stop at EOF from this wrapper. The scratch buffer resizes to the remaining allowed amount when the caller buffer is too large.

## Test signals
Tests cover exact reads, truncating larger data, zero limits, multiple reads across the limit boundary, and a 3 MiB random-data read.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/limit_reader.rs -->
