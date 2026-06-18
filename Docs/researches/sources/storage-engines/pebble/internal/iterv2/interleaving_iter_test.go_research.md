# sources/storage-engines/pebble/internal/iterv2/interleaving_iter_test.go

## Purpose
`interleaving_iter_test.go` provides datadriven, human-readable coverage for `InterleavingIter` behavior.

## Important APIs, Types, And Functions
`TestInterleavingIter` supports `define-points`, `define-spans`, and `iter` commands. It parses point `InternalKey`s, parses `keyspan.Span`s, creates `base.NewFakeIter` and `keyspan.NewIter`, initializes `InterleavingIter`, and runs `RunIterOps`.

## Control Flow
The datadriven file first defines point and span fixtures, then executes iterator command scripts with optional `start`, `end`, `lower`, and `upper` arguments. Output includes returned keys and current spans.

## State And Persistence Behavior
The current points/spans and iterator live in the test closure. Golden behavior persists in `testdata/interleaving_iter`.

## Dependencies And Integration Points
It depends on `datadriven`, `crstrings`, Pebble `base`, `keyspan`, `testkeys`, and `RunIterOps`.

## Risks And Edge Cases
Datadriven tests cover explicit scenarios but not the full state space; the random test complements them. Shared testdata is also used by `TestIter`, so expected output changes can affect multiple suites.

## Test Signals
Golden output signals correct ordering of point and boundary keys, span display, static/dynamic bounds, prefix seeks, and direction changes.
