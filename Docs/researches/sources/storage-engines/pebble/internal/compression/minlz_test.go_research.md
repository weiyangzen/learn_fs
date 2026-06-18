# sources/storage-engines/pebble/internal/compression/minlz_test.go

## Purpose
This file tests MinLZ behavior at and above its maximum block size, including fallback compatibility.

## Important APIs, Types, And Functions
`TestMinLZLargeBlock` creates buffers of `minlz.MaxBlockSize + delta`, compresses with `MinLZFastest`, and decompresses using both the returned algorithm and explicit `MinLZ`.

## Control Flow
For deltas `-1`, `0`, `1`, and a random large positive value, the test fills deterministic bytes, compresses, decompresses into a same-sized buffer, checks equality, clears the buffer, then repeats using a MinLZ decompressor even if compression returned Snappy.

## State And Persistence Behavior
All data is in memory. The test validates behavior important for persisted blocks larger than MinLZ can encode.

## Dependencies And Integration Points
It uses `github.com/minio/minlz`, `GetCompressor`, `GetDecompressor`, MinLZ settings, and `require`.

## Risks And Edge Cases
The boundary around `MaxBlockSize` is the primary risk. The explicit MinLZ decompressor compatibility check is notable and should be preserved if fallback encodings change.

## Test Signals
Successful equality for all sizes and both decompressor choices indicates correct fallback and decode behavior.
