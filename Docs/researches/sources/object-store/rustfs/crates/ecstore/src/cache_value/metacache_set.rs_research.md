# sources/object-store/rustfs/crates/ecstore/src/cache_value/metacache_set.rs

## Purpose
This file implements raw distributed metacache listing over erasure disks. It launches per-disk producers that walk directory metadata into async duplex streams, then a merge consumer compares `MetaCacheEntry` heads across disks, emits agreed entries, emits partial disagreement sets, handles fallback disks, enforces read quorum, and avoids hangs from stalled producers.

## Important APIs, Types, and Functions
- `AgreedFn`, `PartialFn`, and `FinishedFn` are async callback types for agreed entries, partial entries with error state, and final error summaries.
- `ListPathRawOptions` carries disks, fallback disks, bucket/path, recursion and filtering options, quorum (`min_disks`), reporting and limit flags, callbacks, and test-only reader behavior/timeout controls.
- `list_path_raw(rx, opts)` is the main async function.
- `peek_with_timeout` wraps `MetacacheReader::peek` in a timeout and returns `PeekOutcome::{Ready, Error, TimedOut}`.
- `record_producer_error` and `producer_error` share producer failures with the merge consumer through per-disk `OnceLock<DiskError>`.
- Test-only `TestReaderBehavior` simulates EOF, stalls, ignored cancellation, producer errors, and partial output followed by timeout.

## Control Flow and State Behavior
`list_path_raw` rejects an empty disk list with `ErasureReadQuorum`, builds one duplex stream and spawned producer per disk, and creates a shared cancellation token. Each producer calls `walk_dir` with `WalkDirOptions`; if the primary disk is missing or fails, it tries online fallback disks from a local queue clone. Producer failures are recorded for the corresponding disk.

The merge job loops over all readers. For each reader without a stored error, it peeks with a drive stall timeout. EOF-like conditions increase `at_eof`; file/volume not found also count specific not-found counters; timeouts mark that disk failed, increment `rustfs_list_path_raw_stall_total`, log a structured warning, and detach the reader so the loop can continue. Producer-recorded errors are preferred over generic EOF when a writer closes after an error.

The merge logic chooses the lexicographically smallest current entry name. Exact matches across all readers increment `agree`; same-name non-matching entries are partial; greater names wait for later rounds; lower names reset previously selected top entries. If all readers agree, it skips one entry on every reader and calls `agreed`. Otherwise it skips readers that had the selected top entry and calls `partial`.

Quorum exits are explicit. Too many volume-not-found or file-not-found signals return those errors. Too many other errors call `finished`, prefer `Timeout` if any timeout occurred, return a single error if only one exists, or build a combined drive error string. If all readers are EOF or tolerated failures, listing succeeds.

After a successful merge, remaining producers are cancelled and unfinished jobs are aborted before join. Producer join errors and producer disk errors are logged; final producer errors fail only if their count exceeds `disks.len() - min_disks`.

## Dependencies and Integration Points
It depends on disk abstractions (`DiskStore`, `DiskAPI`, `WalkDirOptions`, `DiskError`), `rustfs_filemeta::{MetaCacheReader, MetaCacheWriter in tests, MetaCacheEntry, MetaCacheEntries}`, tokio spawn/duplex/timeout, cancellation tokens, metrics counters, and structured tracing. Higher-level object-listing code can use callbacks to assemble list results from agreed and partial metadata entries.

## Persistence
The code reads persisted object metadata listings from disks through `walk_dir`; it does not write object metadata. Runtime state is in memory: producer tasks, reader buffers, error arrays, and callback invocations.

## Risks and Edge Cases
- Each producer receives its own clone of the fallback disk queue, so multiple failed primaries can select the same fallback disk concurrently.
- `min_disks` drives all quorum math; misconfiguration can either tolerate too much corruption/stall or fail healthy listings.
- Callback errors are impossible because callback futures return `()`, so failures in consumer aggregation cannot be propagated unless encoded externally.
- Lexicographic merge correctness relies on each disk stream being sorted consistently by `MetaCacheEntry.name`.
- Aborting producer tasks is intentional, but disk `walk_dir` implementations must tolerate cancellation/abort.
- Timeouts detach the reader and continue; this avoids hangs but can hide slow-drive data if quorum is still satisfied.

## Test Signals
Inline async tests cover empty disk list, timeout when quorum cannot be met, tolerated stalled reader after quorum EOF, aborting an unresponsive producer, producer timeout after partial output, `peek_with_timeout` timeout/read success, and propagation of producer access denied. These tests strongly signal recent hardening around stalled drives and partial producer failures.
