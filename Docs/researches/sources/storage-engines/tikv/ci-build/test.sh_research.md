# sources/storage-engines/tikv/ci-build/test.sh

## Purpose
`ci-build/test.sh` is a CI test driver that enforces formatting, clippy, test execution, dirty-worktree checks, and panic extraction from logs.

## Important APIs, types, and functions
`panic()` prints an error and exits. The script sets `set -eo pipefail`, changes to the repository root, optionally runs `make format`, uses `git diff-index` to enforce formatting/test cleanliness, traps exit to kill background jobs, sets `RUST_TEST_THREADS` on Travis, and forces `RUSTFLAGS=-Dwarnings`.

## Control flow
After format validation, it runs `make clippy`. It then either runs `make test 2>&1 | tee tests.out` or, with `SKIP_TESTS`, runs `EXTRA_CARGO_ARGS=--no-run make test`. It parses `tests.out` with Python for panic thread names, greps `tests.log` for corresponding cases, and marks status failed if thread panics are found. It cleans logs and exits with accumulated status.

## State and persistence behavior
It writes `tests.out` and `tests.log`, removes `tests.log`, and removes `tests.out` outside Travis. It can leave formatted files changed if `make format` modifies the tree before dirty check.

## Dependencies and integration points
It depends on Bash, make targets, git, Python, and TiKV logging conventions. Environment flags (`SKIP_FORMAT_CHECK`, `SKIP_TESTS`, `SKIP_CHECK_DIRTY_TESTS`, `TRAVIS`) modify behavior.

## Risks and edge cases
The trap kills all background jobs from the shell. Panic-case parsing assumes a specific Rust panic line format and log file field layout. `RUSTFLAGS=-Dwarnings` can fail builds on newly introduced warnings, which is intended but environment-sensitive.

## Test signals
Clean `make format`, `make clippy`, and `make test` runs; dirty-tree detection after formatting/tests; panic extraction from synthetic `tests.out`/`tests.log`; and skip-mode behavior are key signals.
