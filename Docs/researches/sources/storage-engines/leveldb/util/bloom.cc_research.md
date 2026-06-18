# sources/storage-engines/leveldb/util/bloom.cc

## Purpose
`bloom.cc` implements LevelDB's built-in Bloom filter policy for table filters.

## Important APIs, Types, and Functions
`NewBloomFilterPolicy` returns `BloomFilterPolicy`. The policy implements `Name`, `CreateFilter`, and `KeyMayMatch`. `BloomHash` wraps `Hash` with a fixed seed.

## Control Flow
Construction derives the number of probes as `bits_per_key * ln(2)`, clamped to 1..30. `CreateFilter` enforces a minimum 64-bit filter, appends zeroed filter bytes and one byte encoding probe count, then uses double hashing to set bits. `KeyMayMatch` reads encoded probe count and checks all generated bit positions.

## State, Persistence, and Integration
The filter bytes are persisted in filter blocks. The policy name is part of the table metaindex key and must stay stable for compatibility. It integrates with `FilterBlockBuilder` and `Table::ReadMeta`.

## Risks and Test Signals
Changing the policy name or encoding breaks old table filter discovery. Signed-char handling matters when reading the encoded probe count. Tests verify empty/small filters and false-positive rates across sizes.
