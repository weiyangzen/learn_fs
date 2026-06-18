# sources/storage-engines/pebble/internal/itertest/datadriven.go

## Purpose
`itertest/datadriven.go` supplies reusable datadriven command execution for `base.InternalIterator` tests, converting textual commands into iterator operations and formatted output.

## Important APIs, Types, And Functions
`IterOpt` configures `iterCmdOpts`. Options include `Condensed`, `ShowCommands`, `Verbose`, `WithSpan`, and `WithStats`. Formatting helpers are `defaultFormatKV`, `condensedFormatKV`, and `verboseFormatKV`. `RunInternalIterCmd` returns output as a string; `RunInternalIterCmdWriter` writes to an `io.Writer`.

## Control Flow
The runner parses each input line, dispatches commands like `seek-ge`, `seek-prefix-ge`, `seek-lt`, `first`, `last`, `next`, `next-prefix`, `prev`, `set-bounds`, `stats`, `reset-stats`, `is-lower-bound`, and `print`, then formats the returned key/value or error. It tracks the current prefix and previous key to compute `NextPrefix` successor keys.

## State And Persistence Behavior
State is local to one command run: prefix, previous key, formatting options, and optional stats pointer. It mutates the supplied iterator and optional stats but stores no persistent data.

## Dependencies And Integration Points
It depends on `datadriven`, Pebble `base`, `keyspan`, `testkeys`, `blockkind`, `crstrings`, and `testify/require`. Many Pebble iterator tests use it as a common command language.

## Risks And Edge Cases
The command parser assumes non-empty lines and simple whitespace-separated arguments. `next-prefix` requires a previous key and will panic if used after nil. Stats output zeroes nondeterministic timing for stable golden files.

## Test Signals
Stable datadriven outputs across iterator implementations signal consistent seek/next/bounds semantics and error reporting.
