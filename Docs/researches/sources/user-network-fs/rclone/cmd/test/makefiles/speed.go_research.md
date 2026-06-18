<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/makefiles/speed.go -->
# sources/user-network-fs/rclone/cmd/test/makefiles/speed.go

## Purpose

`speed.go` implements `rclone test speed`, a destructive benchmark command that uploads, downloads, and verifies generated files against a remote. It is a test/support command rather than normal sync behavior, but it exercises core copy, cache, check, and cleanup paths.

## Important APIs, Types, and Functions

The command registers `speedCmd` under `cmd/test.Command`. Flags tune `testTime`, `fcap`, `small`, `medium`, `large`, and JSON-only output. `Stats` and `TestResult` describe file size, file count, bytes, duration, and computed `fs.SizeSuffix` speed. `measure` wraps a timed operation, and `speedTest` owns the benchmark lifecycle.

## Control Flow

`RunE` validates one remote, initializes shared test settings, runs an initial four-file 1 MiB probe, then estimates file counts for small, medium, and large test sizes from the slower measured upload/download speed. `speedTest` creates a random remote directory, local generation directory, and local download directory; generates files with `makefiles`; uploads via `sync.CopyDir`; downloads via `sync.CopyDir`; and verifies with `operations.CheckDownload`.

## State and Persistence Behavior

State is temporary but deliberately touches user remotes. Remote and local temporary directories are registered with `atexit.OnError` and purged/removed only when the error sentinel is not overwritten. Successful paths leave no intended durable state; interrupted runs can leave `rclone-speed-test-*` remote directories.

## Dependencies and Integration Points

It integrates with Cobra, rclone test common flags, `cmd.NewFsDir`, fs cache creation, random naming, file generation helpers in the same package, sync copy logic, and operations checking/purge. JSON output is produced with `encoding/json`.

## Risks and Test Signals

Risks include destructive remote writes, cleanup failure on process death, inaccurate sizing when initial samples are noisy, large local disk use from high caps, and divide-by-zero/zero-file skips for very slow remotes. Tests should use small temporary remotes, verify cleanup, cap behavior, JSON shape, integrity check failures, and remote paths with unusual separators.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/makefiles/speed.go -->
