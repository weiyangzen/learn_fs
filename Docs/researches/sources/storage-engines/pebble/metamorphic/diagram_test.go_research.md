# sources/storage-engines/pebble/metamorphic/diagram_test.go

## Purpose
`diagram_test.go` provides datadriven regression coverage for metamorphic ASCII diagram generation.

## Important APIs, types, and functions
The sole test is `TestDiagram`. It runs `datadriven.RunTest` over `testdata/diagram`, handles the `diagram` command, and calls `TryToGenerateDiagram(TestkeysKeyFormat, []byte(d.Input))`.

## Control flow and state behavior
Each fixture input is parsed as metamorphic operations. If diagram generation returns an error, the error string is used as output; otherwise the generated diagram is returned to the datadriven harness. The test has no persistent state and constructs no database.

## Dependencies and integration points
The test depends on the datadriven framework, `TryToGenerateDiagram`, and `TestkeysKeyFormat`. It indirectly covers parser integration, operation `diagramKeyRanges`, formatted operation output, key sorting, and axis spacing.

## Risks and test signals
This is a focused rendering regression test. It does not cover large-input early returns beyond fixture coverage, Cockroach key formatting, or every operation type unless represented in `testdata/diagram`. It is still a useful signal because diagram output is deterministic and easy to diff.
