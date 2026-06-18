# sources/object-store/rustfs/crates/protocols/src/sftp/read_cache.rs

## Purpose
`read_cache.rs` defines the per-handle in-memory read-ahead cache used by SFTP file handles to reduce backend range calls during sequential reads.

## Important APIs, Types, and Functions
`ReadCache` stores a byte buffer, `window_offset`, and a shared `Arc<AtomicU64>` memory accumulator. `new` creates an empty cache. `get(offset, len)` returns a slice when the offset falls inside the cached window, truncating at the window end. `populate(offset, bytes)` replaces the buffer and adjusts the accumulator by old/new `Vec` capacity. `capacity` reports the current buffer capacity, and `Drop` subtracts live capacity from the accumulator.

## Control Flow
The driver checks memory limits before `populate`. Reads are range checks against the active window. A hit near the window end returns only the in-window portion; the next client read refreshes from the backend.

## State and Persistence Behavior
Cache state lasts for an open file handle and is dropped on close or session teardown. Accounting is by `Vec::capacity`, not logical length. Relaxed atomic ordering is used because the counter is an approximate resource guard.

## Dependencies and Integration Points
The module uses standard `Arc` and atomics. `state.rs` embeds it in `HandleState::File`; `driver.rs` creates caches from the shared server accumulator; `read.rs` reads and populates them.

## Risks and Test Signals
Risks include accumulator drift, capacity exceeding payload size, and short reads on partial hits. Tests cover empty misses, hits and misses around window boundaries, partial edge hits, replacing windows, capacity reporting, drop draining, and zero-length gets.
