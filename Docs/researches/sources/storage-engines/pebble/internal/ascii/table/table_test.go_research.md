<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/ascii/table/table_test.go -->
# sources/storage-engines/pebble/internal/ascii/table/table_test.go

## Purpose
This file datadriven-tests the ASCII table renderer.

## Important APIs, Types, And Functions
`TestTable` constructs `Layout` values with `Define`, `String`, `StringWithTupleIndex`, `Int`, and `Div`, toggles `RenderOptions.HorizontalDividers`, and renders into `ascii.Board`.

## Control Flow
Each datadriven command chooses a layout, parses alignment and divider args, optionally filters odd rows, resets the board, renders the table, and returns board text.

## State And Persistence Behavior
The board is reused across commands through `Reset`; no persistent state exists.

## Dependencies And Integration Points
It uses `datadriven`, `strconv`, `testing`, and `internal/ascii`.

## Risks And Edge Cases
Coverage targets tuple-index preservation after filtering, long values exceeding declared widths, no-divider layout, left/right/center alignment, and negative/explicit horizontal dividers.

## Test Signals
Golden datadriven output catches layout regressions, spacing changes, and divider placement changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/ascii/table/table_test.go -->
