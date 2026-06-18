# sources/storage-engines/pebble/internal/treeprinter/tree_printer_test.go

## Purpose
This file validates treeprinter formatting across styles, multiline nodes, Unicode text, nested trees, and omitted-child markers.

## Important APIs, Types, and Functions
`TestTreePrinter` builds a representative tree and compares output under default, compact, and bullet styles. `TestTreePrinterUTF` verifies multiline Japanese text formatting. `TestTreePrinterNested` embeds the formatted output of two treeprinters as child nodes in a third. `TestTreePrinterDotDotDot` validates `DotDotDot` output and connector updates.

## Control Flow and State
Tests build trees through the public `Node` API in depth-first order and compare exact strings after trimming leading fixture newlines. There is no shared state between tests.

## Dependencies and Integration
The file imports `strings` and `testing`. It provides golden coverage for a utility used by other debug/test packages.

## Risks and Gaps
Golden strings are sensitive to whitespace and Unicode box-drawing changes, which is appropriate for this package. Tests do not exercise misuse panics or concurrent calls.

## Test Signals
The exact expected strings define the stable rendering contract. The nested-tree test confirms multiline child strings are a supported integration pattern.
