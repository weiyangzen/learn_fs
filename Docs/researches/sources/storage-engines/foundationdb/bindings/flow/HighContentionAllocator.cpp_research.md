## sources/storage-engines/foundationdb/bindings/flow/HighContentionAllocator.cpp

Purpose: implements FoundationDB directory layer high-contention prefix allocation for the Flow binding.

Important APIs and functions: `_allocate` is the actor implementation; `HighContentionAllocator::allocate` wraps it; `windowSize` selects allocation window sizes of 64, 1024, or 8192 depending on start.

Control flow: allocation reads the latest counter window, atomically increments a counter, advances the window when count pressure exceeds half the window, clears old counters/recent keys with no-write-conflict range where appropriate, then randomly probes recent candidate slots. It writes the candidate recent key with no-write-conflict, waits for latest counter and candidate read, adds a write conflict on unused candidate, and returns the candidate encoded as a tuple.

State and persistence: uses two subspaces: `counters` for window counters and `recent` for recently claimed candidates. The returned value becomes a directory prefix after `DirectoryLayer` prepends content subspace.

Dependencies and integration points: uses `Subspace`, `Tuple`, `deterministicRandom`, transaction atomic add, range reads, reads, sets, conflict keys, and transaction option `NEXT_WRITE_NO_WRITE_CONFLICT_RANGE`.

Risks: concurrency correctness depends on conflict ranges and recent candidate writes. Comments note thread safety would need locking if accessed concurrently outside the expected actor model. Values are interpreted as 8-byte integers and invalid metadata throws.

Test signals: indirectly tested by concurrent directory creation and prefix allocation.
