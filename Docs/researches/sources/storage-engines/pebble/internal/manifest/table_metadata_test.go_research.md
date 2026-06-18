# sources/storage-engines/pebble/internal/manifest/table_metadata_test.go

## Purpose
This test file validates table metadata bound maintenance, debug parsing/formatting, virtual statistic scaling, and memory footprint constraints.

## Important APIs And Tests
- `TestExtendBounds` is datadriven and exercises `ExtendPointKeyBounds`, `ExtendRangeKeyBounds`, overall bound type selection, and `boundsMarker`.
- `TestTableMetadata_ParseRoundTrip` checks point-only, range-only, mixed point/range, whitespace-tolerant parsing, virtual tables, and blob references through `ParseTableMetadataDebug`, `Validate`, and `DebugString`.
- `TestTableMetadata_ScaleStatistic` verifies integer scaling for virtual SSTables, including invalid sizes and overflow-resistant cases.
- `TestTableMetadataSize` asserts `TableMetadata` and `TableBacking` byte sizes on amd64/arm64.

## Control Flow
The bound test parses scripted internal-key ranges, mutates one `TableMetadata`, and emits verbose state after every extension. Roundtrip tests parse debug strings, validate metadata invariants, and compare normalized debug output. Size tests use `unsafe.Sizeof`.

## State And Persistence Behavior
The tests primarily cover in-memory metadata, but debug strings mirror manifest test fixtures and parser behavior used by version debug tests. Virtual scaling indirectly protects persisted size semantics for virtual tables.

## Dependencies And Integration Points
The tests use datadriven fixture `testdata/file_metadata_bounds`, `base` key parsing/formatting, and `testify/require`. Struct-size checks are directly tied to manifest memory amplification.

## Risks And Test Signals
The strongest signals are around mixed point/range bounds and memory footprint. Tests do not exhaustively cover `Validate` corruption paths or refcounting; those are exercised indirectly through version application and release tests.
