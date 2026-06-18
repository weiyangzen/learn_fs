# sources/storage-engines/rocksdb/table/block_based/full_filter_block_test.cc

## Purpose
Tests full-filter block building and reading with both custom plugin filter policies and the built-in Bloom filter policy.

## Important APIs, Types, And Functions
`TestFilterBitsBuilder` serializes fixed32 hashes, `TestFilterBitsReader` scans those hashes, and `TestHashFilter` exposes them as a `FilterPolicy`. `PluginFullFilterBlockTest` and `FullFilterBlockTest` inherit `mock::MockBlockBasedTableTester`. `CountUniqueFilterBitsBuilderWrapper` records unique keys/prefixes while delegating to a real builder. Tests include `PluginEmptyBuilder`, `PluginSingleChunk`, `EmptyBuilder`, `DuplicateEntries`, and `SingleChunk`.

## Control Flow
Tests construct a `FullFilterBlockBuilder`, add keys, finish into a `Slice`, wrap the bytes in `ParsedFullFilterBlock`, construct a `FullFilterBlockReader`, and call `KeyMayMatch`. Duplicate-entry tests add repeated keys and prefixes through fixed prefix extractors and assert the unique-entry accounting before finish.

## State And Persistence Behavior
All table/filter data is in memory. The mock table owns a minimal `BlockBasedTable::Rep`, while `CachableEntry` owns each parsed filter block without real cache handles. Custom filter bytes are simple arrays of fixed32 hashes.

## Dependencies And Integration Points
Uses public/internal filter policy APIs, mock block-based table scaffolding, parsed full filter blocks, fixed-prefix transforms, test harness utilities, and coding/hash helpers. It validates that full-filter code works with non-built-in plugin filters as well as `NewBloomFilterPolicy`.

## Risks And Edge Cases
Empty filter behavior is intentionally conservative at the full-filter reader level. Duplicate tests check the interaction between whole-key filtering and prefix filtering, including empty keys and empty prefixes. The plugin reader provides deterministic negative results, avoiding probabilistic Bloom false positives.

## Test Signals
Expected signals are empty finish output for no keys, `KeyMayMatch` true for inserted keys, false for missing plugin-hash keys, Bloom entry estimates that collapse duplicate `box`, and unique-count assertions for whole-key-plus-prefix additions.
