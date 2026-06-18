## sources/storage-engines/pebble/sstable/block_property_test_utils.go

Purpose: Provides reusable test-only block-property collectors, filters, masking filters, and maximum-suffix extraction for `internal/testkeys`-style suffixed keys.

Important APIs/types/functions: `NewTestKeysBlockPropertyCollector`, `NewTestKeysBlockPropertyFilter`, `testKeysBlockIntervalSyntheticReplacer`, `NewTestKeysMaskingFilter`, `TestKeysMaskingFilter`, `testKeysSuffixIntervalMapper`, `testKeysSuffixToInterval`, and `MaxTestKeysSuffixProperty`.

Control flow: The collector maps point key suffixes and range-key suffixes to `BlockInterval`s. Unsuffixed keys map to universal `[0, MaxUint64)`. The filter builds a `BlockIntervalFilter` over a requested suffix interval. The masking filter wraps the interval filter and updates its lower bound in `SetSuffix`. `MaxTestKeysSuffixProperty.Extract` decodes a table/block interval and emits `@Upper`, matching descending testkey timestamp semantics.

State and persistence behavior: The shared property name is `pebble.internal.testkeys.suffixes`; encoded properties use the same interval format as production block intervals. These utilities do not persist outside tests unless used by test SSTables.

Dependencies and integration points: Depends on `internal/testkeys`, `math`, `strconv`, and block-property primitives. Used by higher-level Pebble tests needing deterministic block-property filters and range-key masking behavior.

Risks: The synthetic replacer panics if the synthetic suffix is less than the original upper bound for non-universal intervals. Testkey suffix ordering differs from ordinary byte ordering, so these helpers are specialized and should not be copied into production collectors blindly.

Test signals: This is support code rather than a test itself; it underpins many block-property and masking tests.
