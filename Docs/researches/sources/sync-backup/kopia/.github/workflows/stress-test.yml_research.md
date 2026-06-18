# sources/sync-backup/kopia/.github/workflows/stress-test.yml

## Purpose
Runs Kopia stress tests on pushes, pull requests, tags, and a two-hour schedule. The job is restricted to the upstream `kopia/kopia` repository.

## APIs, Control Flow, and Integration Points
The workflow checks out full history, installs Go from `go.mod`, executes `make stress-test`, and uploads `.logs/**/*.log` artifacts on every outcome. The Makefile target sets `KOPIA_STRESS_TEST=1`, `KOPIA_DEBUG_MANIFEST_MANAGER=1`, `KOPIA_LOGS_DIR`, and `KOPIA_KEEP_LOGS=1`, then runs `tests/stress_test` and `tests/repository_stress_test` with one-hour timeouts.

## State, Persistence, and Dependencies
Local test state includes logs under `.logs`, Go test cache, and repository data produced by stress tests. Artifacts preserve logs for diagnosis. Concurrency cancels older runs for the same ref.

## Risks and Test Signals
The scheduled cadence is aggressive and may consume CI capacity, but the upstream guard prevents forks from running it. Stress tests can be flaky if they depend on timing, filesystem behavior, or resource availability. The signal is valuable for repository consistency, manifest-manager behavior, and long-running concurrent operations.
