# sources/storage-engines/foundationdb/flow/include/flow/Util.h

## Purpose
Small generic utilities for parsing key/value text, unordered vector removal, scoped counters, and human-readable progress/time formatting.

## Important APIs, Types, And Functions
`keyValueReader` parses line-oriented key/value pairs and stops when the consumer returns false. `swapAndPop` removes an element without preserving order. `Hold<T>` increments/decrements an external counter through RAII. Formatting helpers cover bytes, durations, byte progress, throughput, ETA, elapsed time, and ISO8601 UTC timestamps.

## Control Flow
The reader loops through stream lines, ignores parse failures and trailing text, and calls the consumer on valid pairs. `Hold` mutates on construction/destruction/release. Formatters branch by thresholds and return strings.

## State And Persistence Behavior
Only `Hold` mutates external in-memory state. There is no persistence.

## Dependencies And Integration Points
Uses standard algorithms, streams, strings, time, and C formatting. Included by generic actors and useful for CLI/status/progress output.

## Risks And Edge Cases
`swapAndPop` changes order and assumes valid index. `Hold` is not synchronized. Formatting uses fixed buffers and casts; very large values deserve review. `keyValueReader` reuses parsed variables between lines.

## Test Signals
Malformed line skipping, early stop, move/release behavior, threshold formatting, optional total formatting, and UTC timestamp output.
