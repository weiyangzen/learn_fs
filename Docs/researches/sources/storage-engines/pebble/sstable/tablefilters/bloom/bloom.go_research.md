# sources/storage-engines/pebble/sstable/tablefilters/bloom/bloom.go

## Purpose
Defines Pebble's RocksDB-compatible Bloom table filter policy, hash function, writer, decoder, and policy-name parsing.

## Important APIs, Types, And Functions
`probes` and `calculateProbes` tune probes per bits/key. `hash` implements a RocksDB/LevelDB-compatible Murmur-like 32-bit hash including signed-byte tail behavior. `tableFilterWriter` collects hashes. `FilterPolicy`, `filterPolicyImpl.Name`, `NewWriter`, `PolicyFromName`, `Family`, and `Decoder` expose the table-filter contract.

## Control Flow
Writers call `AddKey`, accumulating hashes while suppressing consecutive duplicates in the collector. `Finish` calculates an odd number of 64-byte cache lines, builds filter bytes, resets the collector, and returns `Family`. Readers select `Decoder` by family and call `mayContain` over the serialized filter.

## State And Persistence Behavior
The policy name and `rocksdb.BuiltinBloomFilter` family are persisted in table metadata/filter blocks. The default 10-bit policy preserves the historical family name for compatibility.

## Dependencies And Integration Points
Integrates with SSTable writer/reader filter plumbing, `tablefilters.PolicyFromName`, adaptive policy parsing, and test fixture generation. Depends on Pebble base filter interfaces and `bits.go`.

## Risks And Edge Cases
Hash compatibility depends on signed-byte tail casting. Bits/key must be at least one. For bits/key above 10, probe count is capped at the simulated optimum table entry. Approximate bits/key is rounded by cache-line granularity and odd line count.

## Test Signals
Bloom tests compare exact small-filter bits, hash outputs from RocksDB, end-to-end FPR, and benchmark construction/probing speed.
