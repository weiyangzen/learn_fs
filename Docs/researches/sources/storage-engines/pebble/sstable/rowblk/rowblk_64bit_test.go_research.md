# sources/storage-engines/pebble/sstable/rowblk/rowblk_64bit_test.go

## Purpose
This 64-bit-only test file verifies row-block writer and iterator behavior for very large blocks near or beyond 4 GiB. It protects against integer overflow in restart offsets, restart table locations, and iterator seek calculations.

## Important APIs, Types, And Functions
`TestSingularKVBlockRestartsOverflow` writes one key/value pair with a 2 GiB key and 2 GiB value, then verifies `SeekGE` and `SeekLT`. `TestExceedingMaximumRestartOffset` writes many 4 MiB values until the block buffer exceeds `MaximumRestartOffset`, then expects an `ErrBlockTooBig` on a subsequent add. `TestMultipleKVBlockRestartsOverflow` writes many entries just below 2 GiB, then a 4 GiB value that moves the restart table offset past `math.MaxUint32`, and verifies seeking earlier keys still works.

## Control Flow
Each test skips under CI and slow/instrumented builds because it needs very large allocations. The tests manually preallocate `Writer.buf` to avoid repeated growth copies, add large entries, finish the block, create a `NewIter`, and validate seek results or writer errors. The multiple-KV test verifies `iter.restarts` exceeds both `MaximumRestartOffset` and `math.MaxUint32` before repeatedly seeking keys.

## State And Persistence Behavior
All state is in memory. No files are written. The tests stress the serialized row-block byte slice produced by `Writer.Finish` and the iterator's interpretation of offsets within that slice. They directly observe `writer.buf` length and `iter.restarts`.

## Dependencies And Integration Points
The file depends on row-block `Writer`, `NewIter`, `MaximumRestartOffset`, `ErrBlockTooBig`, `blockiter.NoTransforms`, Pebble `base.InternalKey`, Go build tags for 64-bit architectures, and build/CI environment checks. It complements normal row-block tests by covering sizes impractical for routine CI.

## Risks
These tests are skipped in common automated environments, so regressions may only be caught in explicit large-memory runs. They intentionally allocate multi-GiB buffers and can cause local memory pressure. Because they inspect internal fields and thresholds, any redesign of restart offset encoding needs corresponding test updates.

## Test Signals
Passing tests indicate row-block iteration handles restart table offsets beyond 32-bit boundaries when individual restart offsets remain legal, and that the writer rejects blocks whose restart offsets exceed the supported maximum. Failures usually point to signed/unsigned overflow, truncation to 32 bits, or missing size checks.
