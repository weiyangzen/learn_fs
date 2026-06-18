# sources/sync-backup/kopia/.github/workflows/endurance-test.yml

## Purpose
Defines the "Endurance Test" GitHub Actions workflow for long-running Kopia endurance coverage. It runs on pushes to `master` and `test/endurance`, tags matching `v*`, a six-hour schedule, and manual dispatch with a `ref` input defaulting to `test/endurance`.

## APIs, Control Flow, and Integration Points
The workflow uses pinned `actions/checkout` and `actions/setup-go`, reads the Go version from `go.mod`, then delegates all test behavior to `make endurance-tests`. The job is guarded with `if: github.repository == 'kopia/kopia'`, so forks do not run the expensive scheduled endurance lane. `KOPIA_KEEP_LOGS=true` is set at job scope, and logs are uploaded from `.logs/**/*.log` through `actions/upload-artifact` under `always()`.

## State, Persistence, and Dependencies
Persistent state is limited to GitHub artifact retention and any logs emitted by the Makefile target. Runtime state comes from the checked-out repository, Go toolchain cache, and generated `.logs` files. The concurrency group is `${{ github.workflow }}-${{ github.ref }}` with cancellation enabled, preventing overlapping endurance runs for the same ref.

## Risks and Test Signals
The main risk is that `workflow_dispatch.inputs.ref` is defined but checkout uses the default ref rather than the input, so manual dispatch may not test the requested branch unless GitHub supplies that ref implicitly elsewhere. The test signal is strong for repository-level endurance behavior because `make endurance-tests` builds an integration binary and runs `tests/endurance_test` with logs preserved.
