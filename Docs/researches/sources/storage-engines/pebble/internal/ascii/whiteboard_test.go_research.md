<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/ascii/whiteboard_test.go -->
# sources/storage-engines/pebble/internal/ascii/whiteboard_test.go

## Purpose
This file tests the ASCII board and cursor write behavior.

## Important APIs, Types, And Functions
`TestASCIIBoardDatadriven` exercises `Make`, `At`, and `WriteString` through testdata commands. `TestASCIIBoard` checks `Printf`, `Reset`, `SetCarriageReturnPosition`, and cursor row/column results.

## Control Flow
The datadriven harness creates boards and writes parsed lines at row/column positions. The direct test writes multi-line strings and verifies rendered output.

## State And Persistence Behavior
Only in-memory board mutation is covered. `Reset` clears the buffer while preserving reusable capacity.

## Dependencies And Integration Points
It integrates datadriven, `crstrings`, `strparse`, and `testify/require`.

## Risks And Edge Cases
The tests focus on automatic row growth, newline handling, and carriage-return column preservation during repeated newlines.

## Test Signals
Golden outputs and direct assertions catch changes in trimming, row growth, and returned cursor positions.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/ascii/whiteboard_test.go -->
