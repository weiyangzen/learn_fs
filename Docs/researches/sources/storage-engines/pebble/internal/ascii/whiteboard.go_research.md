<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/ascii/whiteboard.go -->
# sources/storage-engines/pebble/internal/ascii/whiteboard.go

## Purpose
This file implements a simple growable rune board for rendering ASCII/text diagrams.

## Important APIs, Types, And Functions
`Board` holds a rune buffer and width. `Make`, `At`, `NewLine`, `String`, `Render`, `Reset`, `write`, `repeat`, `growWidth`, `lines`, and `row` manage board storage. `Cursor` provides `Offset`, `Down`, `Right`, row/column setters, `SetCarriageReturnPosition`, `Printf`, `WriteString`, `Repeat`, and `NewlineReturn`.

## Control Flow
Board access grows rows lazily. Writes grow width if needed, handle multi-rune strings, and newline handling returns to a configurable carriage-return column.

## State And Persistence Behavior
State is an in-memory mutable rune grid. `Render` trims trailing spaces per row and prefixes indentation.

## Dependencies And Integration Points
It depends on `bytes`, `fmt`, `slices`, and `strings`. The table renderer builds on `Cursor`.

## Risks And Edge Cases
Width growth must preserve existing rows. Rune indexing avoids byte-width bugs for UTF-8 text, but visual display width is still rune-based, not terminal-cell-width aware.

## Test Signals
`whiteboard_test.go` covers datadriven board commands and newline carriage-return behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/ascii/whiteboard.go -->
