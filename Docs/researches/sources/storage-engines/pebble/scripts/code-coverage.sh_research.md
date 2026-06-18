# sources/storage-engines/pebble/scripts/code-coverage.sh

## Purpose
This script runs Pebble unit tests and metamorphic tests with coverage instrumentation, producing LCOV files for tests, meta tests, and combined coverage.

## Important APIs, Types, and Functions
It runs `go test -tags invariants ./... -coverprofile ... -coverpkg=./...`, builds an instrumented `internal/metamorphic/metarunner`, runs metamorphic tests with `GOCOVERDIR`, converts coverage with `go tool covdata textfmt`, and converts Go coverage to LCOV through `github.com/cockroachdb/code-cov-utils/convert@v1.1.0`.

## Control Flow
The script creates `artifacts`, allocates a temp directory with cleanup trap, records whether either test phase failed, still attempts coverage conversion, and warns at the end if tests failed.

## State and Persistence Behavior
Persistent outputs are `artifacts/profile-tests.gocov`, `profile-meta.gocov`, `profile-tests.lcov`, `profile-meta.lcov`, and `profile-tests-and-meta.lcov`. Temporary metarunner and coverage directories are removed on exit.

## Dependencies and Integration Points
It integrates with Go coverage tooling, Pebble metamorphic tests, `code-cov-utils`, and the publish script.

## Risks
Because it continues after failed tests, generated coverage can be incomplete. It intentionally does not cover crossversion metamorphic tests. Network/module availability is needed for `go run .../convert`.

## Test Signals
The main signal is successful artifact creation; a warning indicates coverage exists but may not represent a clean test run.
