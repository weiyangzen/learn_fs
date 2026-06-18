# sources/storage-engines/foundationdb/bindings/bindingtester/run_tester_loop.sh

## Purpose
This Bash helper runs scripted binding tests once, then loops API/directory binding tests forever across supported languages.

## Important APIs, Types, And Functions
`LOGGING_LEVEL` defaults to `WARNING`. Function `run` invokes `bindingtester.py` for API compare, concurrent API, directory compare, and directory HCA with `--cluster-file fdb.cluster`. Function `scripted` runs scripted tests. `run_scripted` runs scripted tests for Python, Ruby, Java, Java async, Go, Flow, and Swift.

## Control Flow
The script executes `run_scripted`, initializes pass counter `i`, then enters an infinite `while true` loop and runs all test types for each language on every pass.

## State And Persistence Behavior
It writes only process output. The invoked tester mutates the configured FDB cluster by inserting/deleting test keys.

## Dependencies And Integration Points
It expects to be run from a directory containing `bindingtester.py` and `fdb.cluster`, with all language tester artifacts available.

## Risks And Edge Cases
There is no exit condition, error handling, or backoff. Indentation is cosmetic but inconsistent for Swift lines. Failures do not stop the loop unless the shell exits for external reasons.

## Test Signals
The signal is continuous stdout from each bindingtester invocation; operators must monitor failures externally.
