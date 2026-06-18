# sources/sync-backup/kopia/.github/workflows/race-detector.yml

## Purpose
Runs Go unit tests with the race detector for pull requests and pushes to `master`.

## APIs, Control Flow, and Integration Points
The workflow checks out full source history, installs Go from `go.mod`, and executes `make -j2 test UNIT_TEST_RACE_FLAGS=-race UNIT_TESTS_TIMEOUT=1200s`. The Makefile target routes through `gotestsum`, adds `-tags testing`, and runs the repository test suite while skipping the index blob stress test in the regular `test` target.

## State, Persistence, and Dependencies
State is local and transient: Go build/test cache, `.tmp.unit-tests.json`, and any logs from tests. There is no artifact upload. Concurrency cancellation prevents duplicated race runs on the same ref.

## Risks and Test Signals
The race detector materially increases runtime and resource use, which is why the workflow is Linux-only and uses `-j2`. It does not cover all integration targets, but it is an important signal for shared-memory bugs in core Go packages. Missing artifact upload means debugging depends on GitHub logs unless tests persist their own logs elsewhere.
