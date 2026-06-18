# sources/storage-engines/pebble/internal/testutils/indenttree/indent_tree_test.go

## Purpose
This file provides datadriven tests for the indentation tree parser, formatting successful parses as explicit trees and returning parser errors for invalid inputs.

## Important APIs, Types, and Functions
`TestIndentTree` runs over `testdata`. For `parse` commands, it calls `Parse`, then recursively walks returned nodes and renders them under a `<root>` node with `treeprinter.New`.

## Control Flow and State
Each datadriven command is independent. On parse error, the test returns an `error: ...` string for golden comparison. On success, it performs DFS over parsed nodes.

## Dependencies and Integration
The test imports `datadriven` and `treeprinter`. It validates both parser structure and its compatibility with the tree printer.

## Risks and Gaps
The test depends on fixture breadth. It does not expose internal indentation level arrays or offsets, only observable parse tree and error text.

## Test Signals
Golden tree output is the main signal that indentation nesting and sibling detection remain stable.
