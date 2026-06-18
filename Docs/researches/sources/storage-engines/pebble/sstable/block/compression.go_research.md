## sources/storage-engines/pebble/sstable/block/compression.go

Purpose: Defines block compression profiles, on-disk compression indicators, and counters for logical bytes compressed/decompressed by level and block kind.

Important APIs/types/functions: `CompressionProfile`, `CompressionSetting`, `SimpleCompressionSetting`, `AdaptiveCompressionSetting`, `UsesMinLZ`, built-in profiles (`NoCompression`, `SnappyCompression`, `ZstdCompression`, `MinLZCompression`, `FastestCompression`, `FastCompression`, `BalancedCompression`, `GoodCompression`), `CompressionProfileByName`, `CompressionIndicator`, `Algorithm`, `compressionIndicatorFromAlgorithm`, `CompressionCounters`, `ByKind`, and `ByLevel`.

Control flow: Built-in profiles register during package initialization into a case-insensitive map, with duplicate names asserting. Simple profiles use one setting for data/value/other blocks and a 12 percent minimum reduction. Fast/Balanced/Good vary data/value/other settings and adaptive cutoffs. `CompressionIndicator.Algorithm` converts durable trailer bytes to internal compression algorithms, while `compressionIndicatorFromAlgorithm` maps compression results back to trailer bytes.

State and persistence behavior: `CompressionIndicator` constants are explicitly durable file-format bytes and must not be changed. Profile names are user/property-facing and looked up case-insensitively. Counters are in-memory atomics grouped by L5, L6, and other levels and by data/value/other block kinds.

Dependencies and integration points: Depends on `internal/compression`, `base.Level`, `blockkind`, `atomic`, and `errors`. Used by `Compressor`, `PhysicalBlockMaker`, `Reader.doRead`, table options, and compression stats/properties.

Risks: Unsupported compression indicators and algorithms panic/assert. MinLZ format support depends on table format v6+ callers falling back for older formats. Adaptive settings must not equal the `OtherBlocks` setting to be meaningful. Adding block kinds or algorithms requires updating routing and mapping logic.

Test signals: `compressor_test.go` checks per-kind profile routing, `compression_stats_test.go` checks stats formatting/parsing, and `compression_test.go` exercises temp buffers and physical block creation under Snappy.
