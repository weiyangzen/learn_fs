# sources/storage-engines/badger/test.sh

## Purpose
This shell script orchestrates Badger's local/CI test workflow. It runs Go tests with jemalloc tags, optional coverage collection, root tests, a stream benchmark/leak check, and manual memory-intensive tests in sequence.

## Important Functions and Commands
- Global setup prints `go version`, configures CI coverage flags, computes Badger package list via `go list`, and sets `tags="-tags=jemalloc"`.
- It builds the `badger` CLI before test execution.
- `root` runs root package tests with race detector, parallelism 16, timeout 25 minutes, and fail-fast.
- `stream` runs `badger benchmark write/read`, `badger stream`, and checks log output for zero allocated bytes at program end.
- `manual` runs all packages with race detector and a set of `--manual=true` targeted tests, including truncation, large key/value, value log limit, iteration, stream, goroutine leak, and get-more cases.
- `write_coverage` appends package coverage output into `cover.out` in CI.

## Control Flow and State Behavior
The script exits on errors via `set -eo pipefail`. In CI it prepares atomic coverage mode and a shared coverage file. It exports `packages` before setting `GOFLAGS` to preserve `go list` output format. The manual path sets `GOTOOLCHAIN=go1.25.0+auto`, iterates packages, and then runs individual manual tests. At the bottom, parallel execution is commented out; the active order is `root`, `stream`, `manual`.

The stream leak check creates a temp directory under `badger`, runs CLI operations, counts occurrences of `"at program end: 0 B"`, removes the temp directory, and fails unless four zero-allocation lines are present.

## Dependencies and Integration Points
The script depends on Bash, Go tooling, the Badger CLI package under `badger`, jemalloc build tags, `truncate`, and test flags such as `--manual=true`. It integrates with CI coverage collection through `cover.out`.

## Risks and Edge Cases
The script mutates global Go env with `go env -w GOTOOLCHAIN=...` inside `manual`. It assumes leak log text remains stable. Coverage merging uses `sed -i`, which is GNU-specific. Manual tests are expensive and run with race detector, so total runtime can be high. The stream temp directory is removed, but failures before cleanup inside some paths could leave artifacts.

## Test Signals
The script is itself a test runner rather than unit-tested code. Its signal is the sequencing of root, stream/leak, and manual stress tests used by the project.
