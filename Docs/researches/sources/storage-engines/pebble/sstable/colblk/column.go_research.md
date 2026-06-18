<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/column.go -->
# sources/storage-engines/pebble/sstable/colblk/column.go

## Purpose
`column.go` defines the shared type system and interfaces for column encoders/decoders in the columnar block format. It is the small contract layer that lets `block.go` and higher-level block writers compose concrete encodings uniformly.

## Important APIs, Types, And Functions
`DataType` enumerates logical column kinds: invalid, bool, uint, raw bytes, and prefix-compressed bytes. `ColumnWriter` extends `Encoder` with `NumColumns`, `DataType`, and `Finish`, allowing one logical writer to emit one or more physical columns. `Encoder` defines `Reset`, `Size`, and `WriteDebug`. `DecodeFunc[T]` is the typed decoder function signature used by `DecodeColumn`. `Array[V]` is a minimal indexed-access interface, and `Clone` materializes the first `n` values of any `Array`.

## Control Flow
There is no complex control flow. The key contract is size-before-finish: block writers call `Size(rows, offset)` to calculate offsets, then call `Finish(col, rows, offset, buf)` in column order. The `rows` parameter may be the current row count or one less, supporting block writers that decide to split just before the last appended row.

## State And Persistence Behavior
`DataType` values are persisted as one byte per column header in the columnar block envelope. The string names support diagnostics and tests but are not the persisted representation. The interfaces themselves do not own persistent state; implementors such as `UintBuilder`, `RawBytesBuilder`, and `PrefixBytesBuilder` do.

## Dependencies And Integration Points
`block.go` depends directly on these interfaces. `data_block.go`, `index_block.go`, `keyspan.go`, and `key_value_block.go` all implement or consume `ColumnWriter`. Tests use `Clone` to compare decoded arrays against generated expected data.

## Risks
`DataType.String` indexes directly into `dataTypeName`, so invalid out-of-range values can panic rather than return a safe placeholder. Any addition to `DataType` must update `dataTypesCount`, `dataTypeName`, block formatting dispatch, randomized tests, and concrete decoder access paths.

## Test Signals
There is no standalone test file for `column.go`; coverage comes from all block round-trip tests. `block_test.go` especially verifies `DataType` names, `ColumnWriter` composition, and `Clone` through randomized schemas.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/column.go -->
