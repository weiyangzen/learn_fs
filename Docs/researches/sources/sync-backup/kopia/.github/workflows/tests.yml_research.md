# sources/sync-backup/kopia/.github/workflows/tests.yml

## Purpose
Defines the main cross-platform test workflow for pull requests, pushes, tags, and a weekly schedule. It validates unit tests, selected stress coverage, and integration tests across Windows, Linux, macOS, and Ubuntu ARM.

## APIs, Control Flow, and Integration Points
The matrix installs platform prerequisites, runs `make -j4 ci-setup`, then executes `make test-index-blob-v0`, `make ci-tests`, and `make -j2 ci-integration-tests`. `ci-tests` expands to `vet test`; integration tests include robustness tool tests and socket activation tests where platform conditions allow them. Logs from `.logs/**/*.log` are uploaded per matrix OS.

## State, Persistence, and Dependencies
The workflow relies on Makefile-managed Go tools, Node app modules on supported architectures, and platform package managers. It persists logs as artifacts and otherwise keeps test state local. Filename stress options are controlled through secrets.

## Risks and Test Signals
The workflow is broad but still skips or conditions certain expensive or platform-specific targets inside the Makefile. ARM runners may skip UI node module setup because the Makefile limits `app-node-modules` to amd64. The test signal is the primary merge gate for Go unit behavior, index blob stress, vet checks, integration test binaries, socket activation, and robustness tooling.
