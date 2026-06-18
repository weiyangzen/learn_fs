# sources/storage-engines/pebble/internal/itertest/probe_test.go

## Purpose
`probe_test.go` validates the itertest probe DSL and wrapper behavior through datadriven commands.

## Important APIs, Types, And Functions
`TestProbes` creates a parser and mutable `base.InternalIterator` variable. The `new` command parses each input line as a probe and attaches it around the current iterator. The `iter` command runs `RunInternalIterCmd` in verbose mode.

## Control Flow
The test resets the iterator to nil on `new`, attaches probes line by line with a `ProbeState` containing `testkeys.Comparer`, and then drives the resulting wrapper with iterator commands from `testdata/probes`.

## State And Persistence Behavior
State is the current probe-wrapped iterator and a `strings.Builder` that is reset per command. Persistent expectations live in datadriven testdata.

## Dependencies And Integration Points
It depends on `datadriven`, `crstrings`, Pebble `base`, `testkeys`, and the probe/parser helpers in the same package.

## Risks And Edge Cases
Parse errors are returned as command output rather than failing the test immediately, enabling negative golden cases. Starting from nil iterators means many behaviors are probe-driven rather than underlying-iterator-driven.

## Test Signals
Golden outputs confirm parsing, conditional predicates, operation constants, injected errors, nil results, replacement KVs, and verbose command formatting.
