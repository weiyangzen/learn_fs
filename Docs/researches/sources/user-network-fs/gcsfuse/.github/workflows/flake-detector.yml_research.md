## sources/user-network-fs/gcsfuse/.github/workflows/flake-detector.yml

Purpose: Re-runs the Go test suite multiple times on master to detect flaky tests.

Important APIs/types/functions: triggers manually and on push to `master`; single `flake-detector` job on Ubuntu 22.04; installs Go from `.go-version`, FUSE packages, builds gcsfuse, downloads modules, runs `go test -count 5`, and race tests for cache/gcsx with `-count 5`.

Control flow: checkout full history, setup Go without cache, install OS deps, build, download dependencies, then run repeated tests with the flaky skip list for all packages and repeated race tests for selected packages.

State and persistence: no persistent artifacts; results persist as workflow logs/checks.

Dependencies and integration points: uses `flaky_tests.lst`, skip-tests helper, `tools/build_gcsfuse`, Go modules, and FUSE packages.

Risks: because known flaky tests are skipped, this detects new flakes but not regressions in the skipped list. Runtime is capped at 20 minutes and may miss slow flakes. Full-history checkout increases cost.

Test signals: repeated passing or failing GitHub workflow checks on master and manual runs.
