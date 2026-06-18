# sources/storage-engines/leveldb/table/filter_block_test.cc

## Purpose
`filter_block_test.cc` validates the filter block format independently of Bloom filters using a deterministic hash-list policy.

## Important APIs, Types, and Functions
`TestHashFilter` implements `FilterPolicy::CreateFilter` by appending one fixed32 hash per key and `KeyMayMatch` by scanning those hashes. `FilterBlockTest` owns the policy. Tests are `EmptyBuilder`, `SingleChunk`, and `MultiChunk`.

## Control Flow
Tests build filter blocks with `StartBlock` offsets, add keys, finish, then query matching and missing keys through `FilterBlockReader`. Multi-chunk coverage verifies offset-to-filter-index mapping and empty filter slots.

## State, Dependencies, and Integration
The tests depend on `util/hash`, `util/coding`, `FilterPolicy`, and gtest. They prove the table layer can use arbitrary filter policies, not just the built-in Bloom filter.

## Risks and Test Signals
The tests focus on false-negative prevention and empty-region behavior. They do not test corrupt filter blocks, but production reader logic returns true on corruption to preserve correctness.
