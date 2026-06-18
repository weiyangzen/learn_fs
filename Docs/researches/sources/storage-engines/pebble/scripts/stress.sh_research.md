# sources/storage-engines/pebble/scripts/stress.sh

## Purpose
This script stress-tests every Go package in Pebble one package at a time, giving high-state-space packages longer runtimes and lower parallelism.

## Important APIs, Types, and Functions
It loops through `go list ./...`, rewrites module paths to `.`-relative package paths, chooses stress parameters by package, and invokes `make stress STRESSFLAGS=... PKG=...`.

## Control Flow
Root, `internal/manifest`, `internal/metamorphic`, `sstable`, and `wal` get `30m`, `1000` max runs, and `75%` parallelism. Other packages get `5m`, `1000` max runs, and `100%` parallelism. The script stops on first failure through `set -euo pipefail`.

## State and Persistence Behavior
It does not intentionally persist state beyond whatever `make stress` and tests write.

## Dependencies and Integration Points
It depends on Go package listing and the repository's `make stress` target, which likely wraps the stress binary.

## Risks
Running all packages can be expensive. The package classification is hard-coded and may need updates as expensive packages shift. Because packages run serially, early failures prevent later package coverage.

## Test Signals
Success means every listed package passed its assigned stress budget. Command echoes show the exact stress settings per package.
