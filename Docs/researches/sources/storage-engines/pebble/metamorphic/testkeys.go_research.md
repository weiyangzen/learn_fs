<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/testkeys.go -->
## sources/storage-engines/pebble/metamorphic/testkeys.go

Purpose: defines the `testkeys` key format and random key generator used by metamorphic tests to exercise prefix/suffix-aware Pebble behavior, block property filters, masking filters, and MVCC-like suffix ordering.

Important APIs and types: `TestkeysKeyFormat` supplies comparer, columnar key schema, test-key block property collector/filter/mask, formatting/parsing hooks, and generator factory. `testkeyKeyGenerator` implements `KeyGenerator` methods including `RecordPrecedingKey`, `ExtendPrefix`, `RandKey`, `RandKeyInRange`, `RandPrefix`, `SkewedSuffix`, `UniformSuffix`, `SuffixRange`, `IncMaxSuffix`, and helpers for comparison/splitting/parsing.

Control flow: key generation usually reuses known keys unless probabilities choose a new key/prefix. New suffixes are drawn from configured write suffix distributions, with occasional `IncMax` growth. Range-bound generation handles same-prefix suffix ranges and cross-prefix ranges separately, validating the final key lies within bounds. Existing prefixes may be combined with new suffixes; duplicate or out-of-range attempts increase the suffix max and retry.

State and persistence: state lives in `keyManager`, RNG, and mutable `OpConfig` suffix distribution. `RecordPrecedingKey` ratchets the max suffix upward when external prior keys are observed. No data is persisted directly.

Dependencies and integration: depends on `internal/testkeys`, `sstable` test-key block properties, `colblk.KeySchema`, Pebble block property filter interfaces, and metamorphic operation generation.

Risks and edge cases: suffix ordering is descending, so comparisons are non-intuitive and carefully handled by `cmpSuffix`. Range generation has retry fallbacks after 10 attempts. `uniformSuffixInt` uses `Int64N(maxVal)` and assumes a positive max. Generated keys may rarely already exist in bounded mode and are tolerated.

Test signals: parser random tests use this generator heavily; broader metamorphic suites validate generated operation streams.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/metamorphic/testkeys.go -->
