# sources/storage-engines/foundationdb/fdbclient/DataDistributionConfig.cpp

## Purpose

`DataDistributionConfig.cpp` serializes a data-distribution range configuration snapshot into JSON for diagnostics or management output.

## Important APIs And Functions

`DDConfiguration::toJSON(RangeConfigMapSnapshot const& config, bool includeDefaultRanges)` returns a `json_spirit::mValue`. It builds an object with a `ranges` array, `numConfiguredRanges`, `numDefaultRanges`, and `numBoundaries`.

Each range in `config.ranges()` is compared with a default-constructed `DDRangeConfig`. Non-default ranges count as configured; default ranges count separately. The function emits a range object with `begin`, `end`, and `configuration` fields when either `includeDefaultRanges` is true or the range is configured.

## Control Flow

The function is a single pass over the range map snapshot. The map boundary count is taken from `config.map.size()`, while emitted range count depends on `includeDefaultRanges`.

## State And Persistence

No state is mutated. The function snapshots an already materialized `RangeConfigMapSnapshot` into a JSON value. Persistent configuration remains in the range config map elsewhere.

## Dependencies And Integration Points

Dependencies include `fdbclient/DataDistributionConfig.h` for `DDConfiguration`, `DDRangeConfig`, and `RangeConfigMapSnapshot`, plus `json_spirit`. It integrates with status or CLI paths that expose data-distribution range configuration.

## Risks And Test Signals

The default/non-default distinction relies on `DDRangeConfig::operator!=` matching user expectations. If `config.map.size()` includes sentinel boundaries, consumers must treat `numBoundaries` as internal map boundary count rather than emitted range count. Tests should cover empty/default-only snapshots, mixed configured ranges, and `includeDefaultRanges` true/false output shape.
