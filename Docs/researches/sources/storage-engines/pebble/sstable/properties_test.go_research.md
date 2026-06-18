# sources/storage-engines/pebble/sstable/properties_test.go

## Purpose
`properties_test.go` validates SSTable properties decoding, encoding round-trips, and load performance. It anchors generated property handling against both a real table fixture and randomized in-memory properties blocks.

## Important APIs, Types, and Functions
- `TestPropertiesLoad` opens `testdata/hamlet-sst/000002.sst`, constructs a reader, reads the properties block, and compares it with a known `Properties` literal.
- `testProps` is a broad fixture covering deletion counts, range-key counts, filter/index metadata, compression metadata, and user properties.
- `TestPropertiesSave` writes properties with `saveToRowWriter`, decodes them with `rowblk.NewRawIter` and `Properties.load`, and compares results.
- `BenchmarkPropertiesLoad` measures repeated raw-row properties decoding.

## Control Flow
`TestPropertiesLoad` uses the real filesystem fixture, opens it through `vfs.Default`, constructs `newReader`, calls `ReadPropertiesBlock`, clears `Loaded` before comparison, and reports structured diffs through `pretty.Diff`.

`TestPropertiesSave` defines a helper `check1` that writes a properties block with `propertiesBlockRestartInterval`, decodes it through a raw row-block iterator, clears `Loaded`, and compares the original and decoded structures. It first checks `testProps`, then runs 1000 `testing/quick` generated `Properties` values. For randomized values, it normalizes `TopLevelIndexSize` to zero when `IndexPartitions` is zero, matching writer-side omission semantics.

The benchmark builds one encoded properties block from `testProps` and repeatedly creates raw iterators and calls `load`.

## State and Persistence Behavior
The tests confirm that persisted property bytes can be read from both production fixture files and newly encoded row-block data. Clearing `Loaded` before equality checks means the tests assert semantic field values, not exact presence bits. `UserProperties` are included in `testProps`, so user metadata survives encode/decode.

## Dependencies and Integration Points
- Exercises `Reader.ReadPropertiesBlock`, `newReader`, and the fixture table reader path.
- Exercises `rowblk.Writer`, `rowblk.NewRawIter`, and `Properties.saveToRowWriter`.
- Uses `vfs.Default` for fixture IO and in-memory row block buffers for round-trip tests.
- Uses `testing/quick` to stress generated property encodings over many shapes.

## Risks and Edge Cases
- Randomized quick values may include unusual strings and maps, but the test normalizes only one known writer invariant; other writer-side omissions still need targeted coverage when new properties are added.
- The fixture comparison intentionally clears `Loaded`, so it does not protect exact loaded-bit behavior.
- The test focuses on pre-columnar row-block property encoding; columnar property block decoding is exercised through reader tests rather than directly here.

## Test Signals
Strong positive signals are fixture compatibility with an existing SSTable, deterministic round-trip of a broad explicit fixture, 1000 randomized round-trips, and a benchmark tracking decode cost. The tests should be updated whenever generated property fields or mandatory/optional encode rules change.
