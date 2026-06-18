# sources/storage-engines/pebble/internal/keyspan/logging_iter_test.go

## Purpose
Tests the recursive fragment-iterator logging wrapper.

## Important APIs, Types, And Functions
`TestLoggingIter` parses spans, builds `NewIter`, wraps it with `Assert`, then calls `InjectLogging` with `base.InMemLogger`. It runs commands through `RunFragmentIteratorCmd` and normalizes pointer values with a regexp.

## Control Flow
Datadriven `define` loads spans. `iter` creates the stack, executes commands, closes the iterator, obtains logger output, and strips addresses for deterministic golden output.

## State And Persistence Behavior
All logs are held in memory. No external files are written by the test.

## Dependencies And Integration Points
Depends on `datadriven`, `crstrings`, `base.InMemLogger`, `Assert`, and logging wrapper recursion through `WrapChildren`.

## Risks And Edge Cases
The test uses a simple two-layer stack, so deeper or unusual wrappers rely on the same recursion contract but are not exhaustively covered.

## Test Signals
Failures show changed logging tree shape, missing child wrapping, incorrect result formatting, or close-operation logging regressions.
