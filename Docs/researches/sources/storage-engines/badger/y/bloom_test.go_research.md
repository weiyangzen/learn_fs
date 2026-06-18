# sources/storage-engines/badger/y/bloom_test.go

## Purpose
This test file validates Bloom filter bit layout, containment behavior, false-positive rate, and hash compatibility with the LevelDB C++ implementation.

## Important APIs, Types, And Functions
`Filter.String` renders filter bytes as bit characters for fixture comparison. `TestSmallBloomFilter` checks two inserted words against an exact bit string. `TestBloomFilter` builds filters from 1 through 10000 keys and checks size and false positives. `TestHash` checks known hash outputs.

## Control Flow
The main false-positive test increases lengths nonlinearly, hashes little-endian integer keys, builds a filter at 10 bits/key, verifies all inserted keys match, then probes 10000 absent keys. It tracks mediocre versus good filters and fails if too many exceed the tighter false-positive threshold.

## State And Persistence Behavior
The tests are pure in-memory. Their fixtures act as compatibility signals for persisted table filter encodings.

## Dependencies And Integration Points
They directly exercise `Hash`, `NewFilter`, and `MayContainKey`, and indirectly protect table block behavior that depends on these filters.

## Risks And Edge Cases
Map iteration order in `TestSmallBloomFilter` does not affect assertions. The false-positive test is deterministic for generated keys but statistical by threshold. It does not exercise `BloomBitsPerKey`.

## Test Signals
Failures indicate incompatible Bloom encoding, hash drift, excessive filter size, missed positives, or false-positive regression.
