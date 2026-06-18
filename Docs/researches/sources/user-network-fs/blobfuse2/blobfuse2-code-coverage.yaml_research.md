# sources/user-network-fs/blobfuse2/blobfuse2-code-coverage.yaml

## Purpose
This Azure DevOps pipeline collects broad Blobfuse2 Go coverage across unit tests, mounted E2E paths, CLI commands, secure config paths, health monitor commands, proxy paths, and account cleanup.

## Important APIs, Types, and Functions
Parameters are `coverage_test` and `cleanup_test`. It composes `build.yml` and `cleanup.yml`, builds a coverage binary with `go test -coverpkg="./..." -c`, runs many `blobfuse2.test -test.coverprofile=...` commands, runs E2E tests, generates coverage reports with `go tool cover`, publishes build artifacts, and runs `test/scripts/coveragecheck.sh`.

## Control Flow
The `BuildAndTest` stage runs Ubuntu 20 and Ubuntu 22 matrix jobs. It builds containers and binaries, runs unit coverage, builds `blobfuse2.test`, generates block and ADLS configs, mounts with coverage collection including profiler/health-monitor configs, exercises CLI commands for generate, mount/list/unmount, secure encrypt/set, doc, version, config-change simulation, health-monitor stop, and proxy variants, merges `.cov` files while excluding selected packages, publishes reports, checks overall and file-level thresholds, and deletes containers. The `AccountCleanUp` stage optionally installs Go and runs storage account cleanup tests against block and ADLS accounts.

## State and Persistence Behavior
It writes many `.cov`, `.rpt`, and `.html` files, profiler temp configs, secure encrypted configs, proxy logs, mounted data, and Azure test containers. Persistent outputs are published coverage artifacts and cleaned storage accounts.

## Dependencies and Integration Points
It depends on `NightlyBlobFuse`, custom Ubuntu pools, storage accounts, E2E tests, coverage scripts, mitmproxy, and health monitor binary support.

## Risks and Edge Cases
The pipeline is long and stateful, with many background mounts and forced unmounts. Coverage filtering is hard-coded and can hide changed packages. There is a duplicate `workingDirectory` key in the remount test snippet. Proxy environment setup may not apply globally. Secrets are used in generated configs.

## Test Signals
Signals include coverage artifact publication, `coveragecheck.sh` pass, successful block/ADLS/proxy E2E coverage runs, valid health monitor stop coverage, and account cleanup test completion.
