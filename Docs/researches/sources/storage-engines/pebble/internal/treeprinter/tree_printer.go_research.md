# sources/storage-engines/pebble/internal/treeprinter/tree_printer.go

## Purpose
This package builds formatted text trees from depth-first node creation calls. It is used by Pebble debugging and tests to render hierarchical structures.

## Important APIs, Types, and Functions
`Node` is a handle at a specific tree level. `New` and `NewWithStyle` create a root sentinel for `DefaultStyle`, `CompactStyle`, or `BulletStyle`. `Childf`, `Child`, `AddLine`, `AddEmptyLine`, `DotDotDot`, `FormattedRows`, and `String` are the public operations. Internal `tree` stores formatted rows, the current bottom-most path stack, and style-specific edge rune sequences. `set`, `addRow`, and `childLine` update rows and edge connectors.

## Control Flow and State
Callers must add nodes in display order, depth-first pre-order. When a new sibling is added, `childLine` rewrites prior rows to change last-child connectors into mid-child connectors and fill vertical links. Multi-line child text creates a first child line plus additional lines. `AddLine` may shift where future child edges connect. `DotDotDot` appends a hidden-children marker. State is in the mutable `tree` referenced by all `Node` handles; it is not concurrency-safe.

## Dependencies and Integration
The file uses `bytes`, `fmt`, `strings`, and Cockroach errors. It is used by `indenttree` tests and `treesteps` rendering in this work item, and likely by other Pebble debug formatters.

## Risks and Edge Cases
Misordered or stale `Node` use can panic with "misuse of node" or "multiple root nodes". `String` and `FormattedRows` may only be called on the root sentinel. Unicode display width is not measured; runes are counted as columns, which is acceptable for many monospace cases but not all terminals. The output uses Unicode box-drawing characters.

## Test Signals
`tree_printer_test.go` covers default, compact, and bullet styles, UTF text, nesting one tree inside another, and the hidden-children marker.
