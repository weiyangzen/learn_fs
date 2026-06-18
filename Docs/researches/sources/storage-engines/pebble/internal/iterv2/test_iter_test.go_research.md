# sources/storage-engines/pebble/internal/iterv2/test_iter_test.go

## Purpose
`test_iter_test.go` datadriven-tests the `TestIter` reference implementation itself.

## Important APIs, Types, And Functions
`TestTestIter` supports `define-points`, `define-spans`, and `iter` commands, mirroring `interleaving_iter_test.go`. It constructs `TestIterData` with optional `start`, `end`, `lower`, and `upper` arguments and runs `RunIterOps`.

## Control Flow
The test parses fixtures from input lines, prints normalized definitions, constructs a new `TestIter` for each `iter` command, and executes scripted operations.

## State And Persistence Behavior
Points, spans, and the current test iterator are local to the datadriven closure. Golden output lives in `testdata/interleaving_iter`, shared with the interleaving iterator tests.

## Dependencies And Integration Points
It depends on `datadriven`, `crstrings`, Pebble `base`, `keyspan`, and `RunIterOps`.

## Risks And Edge Cases
Using the same testdata as `InterleavingIter` makes comparison easy but means reference and implementation outputs can co-evolve if expectations are changed carelessly.

## Test Signals
Passing tests increase confidence that the reference model’s boundary and span formatting match the intended contract before it is used in random differential tests.
