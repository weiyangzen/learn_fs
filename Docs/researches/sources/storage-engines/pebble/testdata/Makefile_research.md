# sources/storage-engines/pebble/testdata/Makefile

## Purpose
This small Makefile regenerates Pebble test fixture databases under `sources/storage-engines/pebble/testdata`. It provides a single `rebuild` target that removes and recreates four staged database directories using `make-db.go`.

## Important APIs, Types, and Functions
The relevant Make targets are `all` and `.PHONY: rebuild`. `all` aliases to `rebuild`. The `rebuild` recipe loops over stages `1 2 3 4`, removes `db-stage-<stage>`, and runs `go run make-db.go <stage>`.

## Control Flow
Running `make` or `make rebuild` performs a shell loop. Each iteration deletes the previous fixture directory with `rm -fr db-stage-$$stage` and invokes the Go fixture generator for that stage. The Makefile depends on `make-db.go`, so changes to the generator are the explicit reason to rebuild.

## State and Persistence Behavior
The Makefile's only persistent state is the `db-stage-1` through `db-stage-4` fixture directories. It destructively replaces those directories in the testdata tree. The resulting contents are Pebble databases at successive mutation stages and are intended to be checked or consumed as deterministic test fixtures.

## Dependencies and Integration Points
It depends on a working Go toolchain, module resolution for Pebble imports, and the local `make-db.go` program. It integrates with tests or tooling that read the staged `db-stage-*` directories.

## Risks and Edge Cases
The recipe is intentionally destructive for matching fixture names. If run from the wrong directory or with a modified generator, it can rewrite fixture data. It does not set `set -e` explicitly, but the chained `&&` within each loop iteration prevents `go run` after a failed removal and causes make to stop on command failure. Whitespace is minimal; portability assumes POSIX shell behavior.

## Test Signals
The Makefile itself has no tests. A successful `make rebuild` signal is creation of all four `db-stage-*` directories by `make-db.go` without Go runtime errors. Downstream tests that consume these fixtures provide the real validation.
