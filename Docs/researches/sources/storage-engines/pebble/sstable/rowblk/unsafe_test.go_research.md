# sources/storage-engines/pebble/sstable/rowblk/unsafe_test.go

## Purpose
Tests and benchmarks the unsafe varint decoder used by row-block iterators.

## Important APIs, Types, And Functions
`TestDecodeVarint` encodes selected `uint32` values with `binary.PutUvarint` and decodes them through `decodeVarint`. `BenchmarkDecodeVarint` creates random encoded values and repeatedly decodes unsafe pointers while retaining the final pointer to prevent dead-code elimination.

## Control Flow And State
The test covers values across one- through five-byte uvarint lengths, including powers at 7, 14, 21, 28, and 31-bit boundaries. The benchmark stores pointers to allocated five-byte buffers and times only decoder calls.

## Persistence And Integration
No persistent state is written. The benchmark and tests integrate with the performance-critical decoder in `rowblk_iter.go`.

## Risks
The unit test currently prints mismatches instead of failing, so it is weak as a correctness gate. It also does not test malformed or truncated varints; production callers assume valid block bounds. The benchmark uses random time-based data, so exact numbers are not reproducible, though the code path is stable.

## Test Signals
The benchmark is useful for detecting performance regressions in the decoder, while the correctness test should be strengthened to assert equality.
