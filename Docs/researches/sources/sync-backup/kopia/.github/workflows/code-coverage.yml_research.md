# sources/sync-backup/kopia/.github/workflows/code-coverage.yml

Purpose: CI workflow for Go test coverage and Codecov upload.

Important APIs/types/functions: triggers on PR and pushes to master, concurrency cancellation, checkout with full history, setup-go from `go.mod`, `make test-with-coverage`, Codecov upload of `coverage.txt`, and log artifact upload on always.

Control flow: executes tests, uploads coverage, then uploads `.logs/**/*.log` regardless of success.

State and persistence: produces coverage artifact/status and uploaded logs.

Dependencies and integration points: uses `.codecov.yml` policy and Makefile target.

Risks: requires Codecov action/token setup as appropriate; full-history checkout costs time.

Test signals: the workflow itself is a primary test signal.
