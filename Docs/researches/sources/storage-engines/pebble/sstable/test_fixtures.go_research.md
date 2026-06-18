# sources/storage-engines/pebble/sstable/test_fixtures.go

## Purpose
Defines Hamlet-based SSTable fixture data, fixture metadata, and builders for reproducible reader/writer tests.

## Important APIs, Types, And Functions
`testKVs` and `SortedKeys` model expected data. `hamletWordCount` lazily parses `testdata/h.txt`. `hamletNonsenseWords` lists guaranteed misses. `buildHamletTestSST` writes the fixture data plus periodic range deletions. `TestFixtureInfo`, `TestFixtures`, `Build`, fixture size constants, and `fixtureComparer` define fixture variants.

## Control Flow
`hamletWordCount` loads and validates 1710 word-count rows once. Fixture builds sort keys, create a writer with requested compression/filter/comparer/index size/table format, write every key, and mirror `make-table.cc` range deletion generation.

## State And Persistence Behavior
The parsed Hamlet map is cached in package global state. Fixture builds persist SSTables to a caller-provided VFS. The prebuilt fixtures under `testdata` are regenerated from this metadata.

## Dependencies And Integration Points
Used by `table_test.go`, `writer_fixture_test.go`, and `testdata/make-table.go`. Depends on `Writer`, Bloom filter policy, block compression profiles, VFS, and object-storage writable adapters.

## Risks And Edge Cases
Fixture byte equality depends on deterministic writer behavior, compression implementation, and fixed fixture format. The prefix comparer uses full-key split on Hamlet data, which is limited as a prefix-filter stressor.

## Test Signals
Signals are parsed row count, absence of nonsense words in data, successful table reads, and fixture byte-for-byte comparisons.
