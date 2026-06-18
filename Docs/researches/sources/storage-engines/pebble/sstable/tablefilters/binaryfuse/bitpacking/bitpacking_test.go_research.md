# sources/storage-engines/pebble/sstable/tablefilters/binaryfuse/bitpacking/bitpacking_test.go

## Purpose
Validates binary fuse fingerprint bitpacking correctness and provides performance benchmarks for encode and triple-decode operations.

## Important APIs, Types, And Functions
Tests include `TestEncode8_BPV4`, `TestEncode8_BPV8`, `TestEncode16_BPV10`, `TestEncode16_BPV12`, `TestEncode16_BPV16`, `TestDecode_BPV4`, `TestDecode_BPV8`, `TestDecode_BPV10`, `TestDecode_BPV12`, `TestDecode_BPV16`, and `TestRoundTrip`. Benchmarks include `BenchmarkEncode` and `BenchmarkDecode3`.

## Control Flow
Known-value tests encode fixed arrays and compare exact bytes or decode them back. `TestRoundTrip` generates random inputs, encodes for every supported width, checks `Decode` for every index, then samples random triples and checks `Decode3`.

## State And Persistence Behavior
The tests operate entirely on in-memory byte slices. They intentionally prefill encoded buffers to expose missing writes in partial encoders.

## Dependencies And Integration Points
Depends on `math/rand/v2`, `testing`, and `testify/require`. It directly protects the binary fuse filter's persisted fingerprint representation.

## Risks And Edge Cases
Coverage includes odd counts, high bits masking, partial 10-bit/12-bit groups, and little-endian 16-bit output. It does not fuzz malformed encoded data because production callers calculate offsets from trusted filter metadata.

## Test Signals
Signals are exact encoded bytes, equality of decoded masked values, and stable benchmark metrics for Gvals/s and ns/op.
