## sources/user-network-fs/gcsfuse/.github/workflows/ci.yml

Purpose: Main CI pipeline for formatting, generation, build, tests, race tests, coverage upload, and lint.

Important APIs/types/functions: triggers on pushes to `master` and all PR branches. Uses read-only contents permission, branch-aware concurrency, a `filter` job via `dorny/paths-filter`, `format-test`, `linux-tests`, Codecov upload, and PR-only golangci-lint.

Control flow: `filter` determines whether tests should run for non-doc/tool/sample/perf changes. `format-test` always checks generated files, goimports, gofmt, go mod tidy, and clean git diff. `linux-tests` installs FUSE, builds all packages and gcsfuse binary when `run_tests` is true, runs unit tests excluding integration tests with flaky skip list, runs race tests for cache/gcsx packages, and uploads coverage. `lint` runs only off master with new-issues mode.

State and persistence: creates build/test artifacts and coverage output inside the runner; uploads coverage to Codecov.

Dependencies and integration points: relies on `.go-version`, `flaky_tests.lst`, `tools/build_gcsfuse`, `tools/scripts/skip_tests/main.go`, FUSE packages, Codecov token, and golangci-lint action.

Risks: format job runs even for docs-only changes, which may be intended but consumes CI. `paths-filter` predicate `every` with negative patterns should be reviewed carefully to ensure test-skipping matches policy. Coverage config may use singular `unittest` while upload uses `unittests`. `CGO_ENABLED=0` with installed libfuse reflects project build choices but may not catch cgo-specific issues.

Test signals: this workflow is the primary test signal: go generate/tidy diff cleanliness, all package tests, selected race tests, coverage upload, and lint checks.
