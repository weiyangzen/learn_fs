<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cockroachkvs/cockroachkvs.go -->
# sources/storage-engines/pebble/cockroachkvs/cockroachkvs.go

## Purpose
Provides CockroachDB's Pebble key encoding, comparer, formatter/parser, and columnar data-block key schema. It supports Cockroach MVCC keys whose user key is a roach key plus `0x00` sentinel plus optional version bytes and trailing version-length byte.

## Important APIs, Types, and Functions
Public exports include `Comparer`, `EncodeMVCCKey`, `AppendTimestamp`, `EncodeTimestamp`, `NewTimestampSuffix`, `DecodeMVCCTimestampSuffix`, `DecodeEngineKey`, `EncodeKey`, `Split`, `Compare`, `CompareRangeSuffixes`, `ComparePointSuffixes`, `Equal`, `KeySchema`, `FormatKey`, `FormatKeySuffix`, `ParseFormattedKey`, and `ParseFormattedKeySuffix`. Internal components include suffix normalization, `cockroachKeyWriter`, `cockroachKeySeeker`, `suffixTypes`, `validateEngineKey`, and unsafe `memmove`-based materialization.

## Control Flow
Encoding appends a sentinel and optional timestamp/version bytes. Comparison first compares prefix/user key bytes through the sentinel, then compares suffixes in reverse timestamp order; point suffix comparisons normalize away synthetic bits and zero logical components, while range suffix comparison intentionally avoids normalization for historical compatibility. The columnar writer splits keys into roach-key prefix bytes, wall time, logical time, and untyped version columns, tracking which suffix classes are present. The seeker decodes these columns, performs prefix search, then either uses a fast MVCC-only timestamp binary search or a general suffix search. Materialization reconstructs engine keys from decoded columns or applies synthetic suffixes.

## State and Persistence Behavior
The key schema persists columnar block data with a one-byte schema-specific header containing `suffixTypes`. The comparer and formatter are stateless. Unsafe materialization writes directly into iterator buffers and assumes sufficient capacity. Validation enforces terminator length constraints but allows empty keys for separator/index-block cases.

## Dependencies and Integration Points
Integrates with Pebble `base.Comparer`, SSTable columnar block encoding (`colblk`), block iterators, Cockroach MVCC timestamp conventions, Cockroach lock-table key suffixes, and CLI/tool formatting. It uses `crbytes` for common prefixes, invariants for validation, and unsafe metadata casting to fit `cockroachKeySeeker` into `colblk.KeySeekerMetadata`.

## Risks and Edge Cases
Ordering correctness depends on suffix normalization matching Cockroach's engine semantics, including synthetic and zero-logical treatment. Range suffix comparison intentionally differs from point suffix comparison. Unsafe code and `go:linkname` `memmove` require exact buffer sizing and metadata layout. Empty suffix, MVCC suffix, and lock/untyped suffix mixing is rare but handled by a slower path. Parser/formatter panics on invalid human input. `validateEngineKey` permits empty keys but rejects terminator byte `1` and oversized terminators.

## Test Signals
Covered by `cockroachkvs_test.go`, `key_schema_test.go`, `cockroachkvs_64bit_test.go`, and benchmarks. Tests validate comparer properties, separator/successor behavior, writer/seeker datadriven output, lower-bound logic, random block encoding/iteration/seeking, formatting round trips, and metadata size assumptions.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cockroachkvs/cockroachkvs.go -->
