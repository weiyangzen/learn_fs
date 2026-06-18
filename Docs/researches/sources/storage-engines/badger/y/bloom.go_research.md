# sources/storage-engines/badger/y/bloom.go

## Purpose
This utility implements Badger's LevelDB-style Bloom filter encoding and hash function for table block membership checks.

## Important APIs, Types, And Functions
`type Filter []byte` exposes `MayContainKey` and `MayContain`. `NewFilter` builds an encoded filter from precomputed key hashes. `BloomBitsPerKey` estimates bit count from entry count and false-positive rate. `appendFilter` writes filter bits and a trailing probe-count byte. `extend` grows byte buffers. `Hash` is a Murmur-like 32-bit hash.

## Control Flow
Filter creation clamps bits per key, derives probe count `k`, enforces a minimum 64-bit filter, appends zeroed storage, and for each hash sets `k` bit positions by adding a rotated delta. Lookup reverses this logic and returns false when any required bit is absent; unknown future short-filter encodings with `k > 30` are treated as matches.

## State And Persistence Behavior
Filters are immutable encoded byte slices usually stored in table metadata/blocks. The last byte stores the number of probes; preceding bytes store bitset data. No external state is mutated except the provided buffer during append.

## Dependencies And Integration Points
The implementation mirrors LevelDB-Go behavior and is consumed by Badger table lookup code. It depends only on `math`.

## Risks And Edge Cases
Empty or one-byte filters never match. Small key sets get a minimum filter size to avoid high false-positive rates. `BloomBitsPerKey` divides by `numEntries`, so callers must avoid zero entries. Treating unknown encodings as match preserves forward compatibility but can increase false positives.

## Test Signals
`bloom_test.go` verifies bit layouts against C++ LevelDB fixtures, expected hash values, containment for inserted keys, and false-positive rates across filter sizes.
