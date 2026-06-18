<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/cockroachkvs/blockproperties.go -->
# sources/storage-engines/pebble/cockroachkvs/blockproperties.go

## Purpose
Defines CockroachDB-specific SSTable block property collectors and filters for MVCC wall-time intervals. These properties enable Pebble readers to skip blocks outside timestamp constraints and support suffix replacement for synthetic suffixes/range-key masking.

## Important APIs, Types, and Functions
`BlockPropertyCollectors` constructs a block interval collector named `MVCCTimeInterval`. `NewMVCCTimeIntervalFilter` creates a half-open wall-time filter `[minWallTime, maxWallTime+1)`. `MVCCWallTimeIntervalRangeKeyMask` wraps `sstable.BlockIntervalFilter` and sets intervals from range-key suffixes. `MVCCBlockIntervalSuffixReplacer` maps synthetic suffix replacement to a single-wall-time interval. `pebbleIntervalMapper` maps point and range keys to intervals through `mapSuffixToInterval`. `MaxMVCCTimestampProperty.Extract` extracts a maximum suffix-like timestamp from encoded block interval properties.

## Control Flow
Point keys map their user key's encoded MVCC suffix to a `{Lower: wall, Upper: wall+1}` interval. Range keys union the intervals of each suffixed range key. Empty or non-MVCC suffixes map to empty intervals. Filters compare block intervals against requested wall-time ranges. Maximum suffix extraction decodes the interval property and encodes `interval.Upper` as a wall-time-only suffix.

## State and Persistence Behavior
Collectors persist encoded block interval properties in SSTables. Filters and masks are in-memory reader-side state. The half-open interval encoding intentionally stores `Upper` one greater than the largest wall time.

## Dependencies and Integration Points
Depends on `sstable` block property APIs and timestamp decoding from `cockroachkvs.go`. Integrates with CockroachDB MVCC scans, range-key masking, synthetic suffix replacement, and maximum suffix property use in table/block metadata.

## Risks and Edge Cases
`NewMVCCTimeIntervalFilter` adds one to `maxWallTime`, so `math.MaxUint64` would overflow. `ApplySuffixReplacement` returns an assertion failure if synthetic suffix decoding fails. `mapSuffixToInterval` must distinguish full engine keys from bare suffixes using the sentinel index; malformed keys return errors. `MaxMVCCTimestampProperty` encodes `Upper`, not `Upper-1`, to remain a valid upper bound under logical timestamp ordering.

## Test Signals
Direct tests are not in this file, but Cockroach key-schema and SSTable tests indirectly exercise suffix decoding and ordering. Dedicated tests should verify interval collection for wall-only/logical/synthetic timestamps, non-MVCC suffix exclusion, range-key unioning, max timestamp extraction, and overflow behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/cockroachkvs/blockproperties.go -->
