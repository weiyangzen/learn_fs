<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/ascii/table/examples_test.go -->
# sources/storage-engines/pebble/internal/ascii/table/examples_test.go

## Purpose
This file provides a Go example for the generic ASCII table renderer.

## Important APIs, Types, And Functions
`ExampleDefine` uses `table.Define`, `String`, `Int`, `Div`, `Render`, `RenderOptions`, and `ascii.Make`.

## Control Flow
The example defines a struct, creates a table layout with dividers, renders rows into an ASCII board, and prints the board.

## State And Persistence Behavior
No persistent state exists; rendering mutates only the in-memory board.

## Dependencies And Integration Points
It demonstrates the public table package from an external test package and its integration with `internal/ascii`.

## Risks And Edge Cases
As an executable example, output changes are API-visible for docs and tests. It also demonstrates widening beyond the initial board width.

## Test Signals
The `// Output:` block is checked by `go test`, validating exact rendered layout.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/ascii/table/examples_test.go -->
