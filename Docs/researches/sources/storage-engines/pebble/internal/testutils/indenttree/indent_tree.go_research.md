# sources/storage-engines/pebble/internal/testutils/indenttree/indent_tree.go

## Purpose
This package parses indentation-based text into a forest of nodes for test inputs. It provides a compact way to express hierarchies in datadriven fixtures.

## Important APIs, Types, and Functions
`Parse(input)` returns `[]Node` or an error. It validates non-empty input, rejects empty lines and tab indentation, computes the distinct indentation levels, and recursively constructs nodes. `Node` stores a line value and children. `Value()` and `Children()` expose those fields.

## Control Flow and State
`Parse` trims one trailing newline, splits lines, records leading-space counts, sorts and compacts indentation levels, then recursively partitions ranges of lines into sibling and child regions. Indentation must be consistent with discovered levels, and skipped levels cause an error. There is no persistent state.

## Dependencies and Integration
It uses `slices`, `strings`, and Cockroach errors. The test file renders parsed nodes through `treeprinter`, so this parser integrates with Pebble's textual tree debugging tools.

## Risks and Edge Cases
The leading-space loop uses `line[level:]` while incrementing `level`; because it checks empty lines after the loop, all-space lines are handled as errors. Tabs anywhere at the first non-space indentation position are rejected. The parser treats all distinct indentation widths as levels, so accidental inconsistent sibling indentation fails during recursion.

## Test Signals
`indent_tree_test.go` uses datadriven fixtures to parse inputs and render the result, including error cases from invalid indentation.
