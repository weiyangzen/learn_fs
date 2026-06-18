# sources/storage-engines/pebble/metamorphic/example_test.go

## Purpose
`example_test.go` is an executable documentation example for running a Pebble metamorphic test end to end. It demonstrates generating random options and operations, constructing a test, executing it, and expecting a nil error.

## Important APIs, types, and functions
The file defines `ExampleExecute`. It uses `metamorphic.RandomOptions`, `metamorphic.GenerateOps`, `metamorphic.DefaultOpConfig`, `metamorphic.New`, and `metamorphic.Execute`.

## Control flow and state behavior
The example fixes a seed, creates a `math/rand/v2` PCG RNG, selects `TestkeysKeyFormat`, generates options and 10,000 operations, constructs a test with no explicit directory and `io.Discard` output, executes it, and prints the error. The expected output is `<nil>`, so Go's example runner verifies that the execution succeeds.

State is created inside the metamorphic test harness, including temporary DB/test resources managed by `New` and `Execute`. This file itself persists nothing and writes only to the example output stream.

## Dependencies and integration points
The example imports the public `github.com/cockroachdb/pebble/metamorphic` package from an external-test package, which validates that the public-facing metamorphic API is usable outside the package. It also links config defaults from `config.go` to actual execution.

## Risks and test signals
This is a broad smoke test, not a diagnostic unit test. It can catch broken public API wiring or severe execution regressions, but failures may be expensive to localize. Because the seed is fixed, it is deterministic, but it only samples one generated workload.
