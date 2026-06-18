# sources/storage-engines/pebble/objstorage/objstorageprovider/readahead.go

Purpose: This file implements shared dynamic readahead state used by local VFS read handles and remote read handles. It decides when sequential reads justify issuing prefetch/read-ahead and when random or far-away reads should reset the state.

Important types and functions: `readaheadState` tracks `numReads`, `maxReadaheadSize`, current `size`, `prevSize`, and `limit`. `makeReadaheadState` initializes state with `initialReadaheadSize` and caller-provided maximum. `maybeReadahead` returns a positive prefetch size when a read should trigger readahead. `recordCacheHit` feeds cache-hit positions into the same sequentiality model without issuing I/O. Both use `maybeReadaheadOrCacheHit`.

Control flow: The algorithm requires at least `minFileReadsForReadahead` sequential-ish reads before returning a prefetch size. It considers reads that overlap or advance beyond `limit` but remain within `maxReadaheadSize` as sequential. When readahead is issued, it updates `limit`, records `prevSize`, and doubles `size` up to the maximum. Reads within the previous readahead window increase `numReads` but do not issue another prefetch. Reads too far before or after the active window reset to one observed read.

State and persistence: The state is in-memory per read handle. It does not persist across handles or process restarts.

Dependencies and integration: It depends on `internal/invariants` to catch uninitialized state. Local VFS handles translate returned sizes into `Prefetch` or OS sequential reopens. Remote handles translate them into larger buffered object reads.

Risks and test signals: The main risk is off-by-one/window logic causing excessive prefetching or missing sequential reads after cache hits. Data-driven tests in `readahead_test.go` cover reset, cache-hit, sequential, random, and growth behavior by inspecting internal state after each command.
