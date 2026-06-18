# sources/storage-engines/pebble/sstable/tablefilters/bloom/bits.go

## Purpose
Implements cache-line-oriented Bloom filter bit storage, serialization, construction, and membership probing compatible with RocksDB full-file filters.

## Important APIs, Types, And Functions
Constants `cacheLineSize` and `cacheLineBits` define 64-byte lines. `filterBits` aliases raw bytes with a line count. `aliasFilterBits`, `cacheLine`, `probe`, `set`, `buildFilter`, and `mayContain` implement the bit-level behavior.

## Control Flow
`buildFilter` allocates `nLines*64 + 5` bytes, sets all probes for every collected hash within one cache line, then appends one byte of probe count and four bytes of line count. `mayContain` parses this trailer, validates expected cache-line sizing, aliases the bit region, and probes all bits for the candidate hash.

## State And Persistence Behavior
The filter bytes are persisted in SSTables as bit data plus a 5-byte trailer. `filterBits` is just a transient unsafe alias over the byte slice.

## Dependencies And Integration Points
Used by Bloom writer, adaptive writer, decoder, simulations, and tests. Depends on `encoding/binary`, `unsafe`, and CockroachDB errors.

## Risks And Edge Cases
The code performs unsafe aliasing and panics if the serialized line sizing is inconsistent. Corrupt filters with zero line count could misbehave before validation. All probes remain within one cache line for locality, which drives FPR/probe tuning.

## Test Signals
Bloom unit tests verify exact small-filter bytes, inserted-key membership, false-positive bounds, and RocksDB-compatible hash expectations.
