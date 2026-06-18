# sources/distributed-fs/tahoe-lafs/src/allmydata/test/test_netstring.py

## Purpose
Tests Tahoe byte-oriented netstring encoding and fixed-count splitting.

## APIs / Types / Functions
- `netstring(data)` returns length-prefixed bytes.
- `split_netstring(data, count, required_trailer=None)` parses a fixed number of netstrings and returns decoded bytes plus consumed offset.

## Control Flow
Tests verify encoding of `b"abc"`, splitting two adjacent netstrings, required trailer handling, wrong count failures, ignored extra data when no trailer is required, successful non-empty trailers, and nested netstring payload parsing.

## State And Persistence
All state is local bytes. No external resources are used.

## Dependencies / Integration Points
Protects low-level Tahoe serialization/framing helpers where byte exactness and trailer validation matter.

## Risks And Test Signals
Malformed length and partial-input cases are not covered here. Passing tests show stable byte encoding, count-aware parsing, trailer enforcement, and nested payload compatibility.
