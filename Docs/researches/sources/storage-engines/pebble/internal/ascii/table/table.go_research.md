<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/ascii/table/table.go -->
# sources/storage-engines/pebble/internal/ascii/table/table.go

## Purpose
This file implements a generic ASCII table layout and rendering helper over `ascii.Board`.

## Important APIs, Types, And Functions
`Define`, `Layout`, `HorizontalDividers`, `MakeHorizontalDividers`, `RenderOptions`, `Render`, `Element`, `Field`, `Div`, `Literal`, alignment constants, `String`, `Int`, `Int64`, `StringWithTupleIndex`, `AutoIncrement`, `Count`, `Bytes`, `Float`, `makeFuncField`, and `humanizeFloat` define the table API.

## Control Flow
`Render` filters tuples, renders fields column by column, inserts one-space separators, draws dividers and horizontal lines, widens columns for long values, pads by alignment, and returns the cursor after the rendered table.

## State And Persistence Behavior
`Layout` stores field definitions and optional filter function. Rendering only mutates the supplied `ascii.Board`.

## Dependencies And Integration Points
It depends on `internal/ascii`, humanized count/byte formatting, constraints, and Cockroach errors for assertions.

## Risks And Edge Cases
Header width is enforced at `Define` time, but data values can widen columns. Negative horizontal divider indexes count from the end after filtering. Multi-byte strings use rune counts for padding.

## Test Signals
`table_test.go` uses datadriven tests for alignment, dividers, filtering, tuple indexes, and widening; `examples_test.go` checks documented output.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/ascii/table/table.go -->
