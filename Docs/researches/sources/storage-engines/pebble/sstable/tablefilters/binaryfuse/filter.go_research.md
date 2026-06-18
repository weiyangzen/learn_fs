# sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/filter.go

## Purpose
Builds and probes binary fuse filter byte encodings. It manages builder memory reuse/concurrency limits, constructs filters with the external xorfilter library, packs fingerprints, appends the trailer, and implements zero-allocation membership checks over packed data.

## Important APIs, Types, And Functions
Constants `maxSizeForPool`, `maxSizeForReuse`, and `maxSize` define regimes. `globalState`, `builder`, `ensureInitialized`, `builderPool`, and `withBuilder` coordinate reusable builders and a semaphore. `buildFilter`, generic `build[T]`, `mayContain`, and `murmur64` implement filter construction and lookup. `trailerLen` is 14 bytes containing seed, segment count, segment shift, and fingerprint width.

## Control Flow
`buildFilter` rejects empty and too-large collectors, gathers hash blocks into a builder slice, selects `uint8` or `uint16` fingerprints, and calls `BuildBinaryFuse`. The result fingerprints are bitpacked, then seed/segment metadata is appended. `mayContain` parses the trailer, recomputes the binary fuse probe positions from the hash plus seed, decodes three packed fingerprints, and compares their xor with the target fingerprint.

## State And Persistence Behavior
The persisted filter is packed fingerprint bytes followed by a fixed trailer. Builder pools and reusable builders are process-local memory optimizations. No persistent state exists outside SSTable filter bytes.

## Dependencies And Integration Points
Depends on `github.com/FastFilter/xorfilter`, `fifo.Semaphore`, `bitpacking`, `runtime.GOMAXPROCS`, and `hashCollector`. It is invoked by `tableFilterWriter.Finish` and `Decoder.MayContain`.

## Risks And Edge Cases
Builder memory is large, so concurrency throttling is correctness-adjacent for resource pressure. Construction can theoretically fail for small sets and returns `ok=false`. `mayContain` trusts trailer consistency and packed data size enough to decode positions, so corrupted filters may panic if metadata is nonsensical.

## Test Signals
`TestBuildFilter`, end-to-end filter tests, simulations, and benchmarks validate no false negatives, expected FPR shape, and performance across sizes.
