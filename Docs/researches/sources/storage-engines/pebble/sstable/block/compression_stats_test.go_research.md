## sources/storage-engines/pebble/sstable/block/compression_stats_test.go

Purpose: Verifies `CompressionStats` text representation, parse round trips, unknown-setting compatibility, and old-format compatibility.

Important APIs/types/functions: `TestCompressionStatsString`, `TestCompressionStatsRoundtrip`, `TestParseCompressionStatsUnknown`, and `TestParseCompressionStatsOldFormat`.

Control flow: The string test incrementally adds no-compression, Snappy, MinLZ, ZSTD1, and ZSTD3 records and checks exact string ordering/aggregation. The round-trip test randomly selects subsets of settings and random byte sizes, serializes and parses after each addition, and expects canonical string equality. Unknown parsing feeds settings such as `MiddleOut10` and `Magic`, expecting them combined into an `unknown` entry. Old-format parsing accepts `NoCompression:x/x` and rewrites it to `None:x`.

State and persistence behavior: These tests protect the user-property format that may be stored in SSTables and later read by newer versions.

Dependencies and integration points: Uses `math/rand/v2`, `internal/compression`, and `stretchr/testify/require`.

Risks: The randomized test is nondeterministic and does not record a seed. It focuses on successful parse paths, not malformed input cases.

Test signals: Strong compatibility signal for canonical formatting and backward/forward handling of compression setting names.
