# sources/storage-engines/pebble/metamorphic/diagram.go

## Purpose
`metamorphic/diagram.go` generates compact ASCII diagrams of key ranges touched by metamorphic operations. It is a debugging aid for understanding generated operation sequences and their key-space overlap.

## Important APIs, types, and functions
`TryToGenerateDiagram` parses operation text and returns a diagram string or an empty string when the input is too large or has no diagrammable ranges. `genAxis` builds the axis row, label row, and key-to-column map.

## Control flow and state behavior
`TryToGenerateDiagram` parses operations with key-format-specific parsers, rejects large operation counts above 200, collects all range start/end keys from each operation's `diagramKeyRanges`, sorts the key set with the key format comparer, and calls `genAxis`. If the axis would exceed 200 columns, it returns an empty string. It then renders one row per operation with `|---|` range markers followed by the formatted operation string, and appends the axis rows.

`genAxis` spaces labels by at least two columns and key markers by at least four columns, returning deterministic positions for sorted keys. State is entirely local and in-memory.

## Dependencies and integration points
The file depends on the metamorphic parser, operation formatting methods, `KeyFormat`, sorted-key helpers, and standard `strings.Builder`. It is exercised by datadriven tests and useful when diagnosing generated histories.

## Risks and test signals
Risks are mostly usability issues: unreadable spacing, oversized diagrams, parse failures, or incorrect key ordering under custom comparers. `diagram_test.go` covers fixture-based rendering with `TestkeysKeyFormat`. Cockroach key formatting is supported by the API but not directly covered by this file's small test.
