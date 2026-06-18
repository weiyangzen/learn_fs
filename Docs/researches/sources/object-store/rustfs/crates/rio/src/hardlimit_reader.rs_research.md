<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/hardlimit_reader.rs -->
# sources/object-store/rustfs/crates/rio/src/hardlimit_reader.rs

## Purpose
Implements an exact-length `AsyncRead` wrapper. It allows exactly the declared number of bytes, reports `IncompleteBody` if the inner stream ends early, and rejects any bytes beyond the limit.

## Important APIs, types, and functions
- `HardLimitReader<R>::new(inner, limit)` creates the wrapper.
- `remaining` tracks bytes still required.
- `AsyncRead::poll_read` enforces underflow and overflow behavior.
- Capability delegation is provided through `delegate_reader_capabilities_generic!`.

## Control flow
If `remaining` is negative, reads fail. If `remaining` is zero, the wrapper probes the inner reader with an 8 KiB discard buffer: true EOF succeeds, but any extra byte returns an error. Otherwise it polls the inner reader into the caller buffer, subtracts the number of newly read bytes, returns `UnexpectedEof` with `IncompleteBody` if EOF occurs while bytes are still required, and errors if the read overshoots the limit.

## State and persistence behavior
State is the in-memory remaining byte count. It does not persist data, but it is a boundary guard for persisted object writes: data shorter or longer than declared content length should not become accepted object payload.

## Dependencies and integration points
Depends on Tokio `AsyncRead`, `pin_project_lite`, and the local `IncompleteBody` error. `HashReader` wraps positive-size inputs with `HardLimitReader`; encryption/decryption and HTTP streams can sit inside or outside this guard. Tests use `rustfs_utils::read_full`.

## Risks and edge cases
The wrapper must be polled after exactly reading the declared bytes to detect extra input; callers that stop immediately after the limit may miss trailing bytes. It can also block waiting for the overflow probe if the underlying stream remains open. The error for too many bytes is a generic `Other` error string rather than a typed size error.

## Test signals
Tests cover normal reads, exact limits, exceeding limits, empty streams, short input producing `UnexpectedEof` with an `IncompleteBody` marker, and rejection of extra bytes after the limit has been consumed.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/rio/src/hardlimit_reader.rs -->
