# sources/storage-engines/foundationdb/bindings/go/src/fdb/directory/allocator.go

## Purpose

`allocator.go` implements the Go directory layer’s high-contention allocator. It allocates short, mostly random subspace prefixes for new directories while minimizing conflicts under many concurrent creators.

## Important APIs, Types, and Functions

`highContentionAllocator` contains two subspaces: `counters` for allocation-window counters and `recent` for candidate-prefix markers. `newHCA` derives those subspaces from a parent allocator subspace. `windowSize` grows allocation windows from 64 to 1024 to 8192 as the start value increases. `allocate` is the core routine that returns `s.Sub(candidate)` for a free candidate prefix inside the current window.

`oneBytes` is the little-endian encoded increment used with FDB atomic `Add`. `allocatorMutex` serializes certain in-transaction mutation/read setup sequences inside this process.

## Control Flow

`allocate` first snapshots the highest counter key to find the current window start. It increments the current window counter with no write conflict, reads the count, and advances to a larger window if the count indicates the window is at least half full. When advancing, it clears older counter and recent marker ranges.

Once a suitable window exists, it repeatedly chooses a random candidate, writes a marker under `recent` with no write conflict, checks whether a newer window appeared, then reads the candidate marker. If the marker was absent, it adds a write conflict key and returns the candidate subspace. If a newer window appeared or the candidate was already present, it retries.

## State and Persistence Behavior

Allocator state is stored in FoundationDB under the allocator’s `counters` and `recent` subspaces. Counter increments are atomic additions; recent markers reserve candidate prefixes. Clearing older ranges bounds metadata as windows advance. The returned subspace itself is not persisted by this file; callers persist it as directory metadata.

## Dependencies and Integration Points

The allocator depends on the Go `fdb` transaction API, `subspace`, little-endian `encoding/binary`, `math/rand`, and process-local synchronization. It is used by directory layer creation code when a directory needs an automatically assigned content prefix.

## Risks

Randomness uses the package-level `math/rand` source, so deterministic seeding or concurrency behavior can affect allocation patterns. The process-local mutex only coordinates goroutines in one process; correctness still depends on FDB conflict ranges across clients. Byte decoding assumes little-endian counter values matching `oneBytes`. Bugs here can cause prefix collisions or excessive conflicts, making directory creation unsafe or slow.

## Test Signals

Useful tests create many directories concurrently and assert unique prefixes, low conflict rates, correct window advancement, bounded old metadata cleanup, and compatibility with other language directory layer allocators.
