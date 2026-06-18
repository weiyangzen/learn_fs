# sources/storage-engines/pebble/metamorphic/options_test.go

## Purpose
`options_test.go` validates option serialization/parsing, initial-state setup, block-property collector wiring, and custom test option support for the metamorphic harness.

## Important Tests and Helpers
- `TestSetupInitialState` builds a small on-disk Pebble DB, then checks `setupInitialState` clones its directory contents into the configured test FS.
- `TestOptionsRoundtrip` serializes every standard option and 100 random options, parses them back, reserializes, compares closure return values, and diffs `pebble.Options` while ignoring inherently non-comparable fields.
- `expectEqualFn` and `expectEqualValue` compare closure outputs, structs, and approximate float64s.
- `TestBlockPropertiesParse` runs generated ops through one `RunOnce`, walks produced SSTs, opens them, and asserts the default block-property collector wrote user properties.
- `TestCustomOptionParser` validates custom parser registration, custom option serialization through `optionsToString`, and reparse retention.
- `testCustomOption` is a simple `CustomOption` implementation.

## Control Flow and State
The round-trip test starts from `optionsToString`, parses into `defaultTestOptions`, and requires the serialized string to be stable. It then checks specific closure-valued fields including value blocks, ingest-as-flushable, ingest split, compaction concurrency, tombstone thresholds, value separation, deletion pacing, per-level compression/filter policy, max downloads, and block-property collector count.

`TestBlockPropertiesParse` creates a temporary meta directory, writes an `ops` file and a run `OPTIONS` file, executes `RunOnce` with `KeepData`, then scans the `data` directory for `.sst` files and opens them with the same reader options to find the collector property.

## Dependencies and Integration Points
The file uses real Pebble DB open/write/flush/close operations, VFS default and mem filesystems, `testkeys`, object storage readable wrappers, sstable readers, `pretty.Diff`, and the metamorphic `RunOnce` path. It is the main direct test for `options.go` and also lightly exercises `generator.go`, `ops.go`, and `meta.go`.

## Risks and Edge Cases
- Some option fields are ignored in diffs because they are pointers, closures, floats, or otherwise expected to differ by identity after parsing.
- Random options are time-seeded, so failures may need test logs to reproduce the serialized option.
- `TestBlockPropertiesParse` depends on generated operations producing at least one SST with the property; it uses 10k ops and archive cleaner to reduce flakiness.
- Initial-state cloning coverage checks directory entries but not every WAL recovery compatibility branch.

## Test Signals
Passing tests show `OPTIONS` files are stable, random option coverage remains parseable, default block-property collectors are active, and custom options survive the serialize/parse cycle.
