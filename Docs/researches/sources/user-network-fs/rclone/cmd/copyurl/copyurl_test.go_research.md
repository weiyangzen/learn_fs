<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/copyurl/copyurl_test.go -->
# sources/user-network-fs/rclone/cmd/copyurl/copyurl_test.go

## Purpose

`copyurl_test.go` unit-tests single URL and CSV batch control flow for `copyurl` with a mocked copy function.

## Important APIs, Types, and Functions

`resetGlobals` restores package flag globals and `copyURL`. Tests cover missing destination without stdout, explicit filename success, auto filename error propagation, incompatible CSV flags, and CSV fan-out with mixed success/failure.

## Control Flow

Tests set globals, create temp files/directories, replace `copyURL`, invoke `run` or `runURLS`, then assert calls, arguments, and aggregate errors.

## State and Persistence Behavior

The tests write a temporary CSV and local destination directory only. `copyURL` is mocked, so no network or remote writes occur.

## Dependencies and Integration Points

It imports the local backend for destination Fs resolution and uses `testify`, atomics, mutexes, and temp filesystem helpers.

## Risks and Test Signals

Signals cover flag combinations and parallel CSV calls. Gaps include `--stdout` success, header filename behavior, no-clobber, actual HTTP integration, CSV malformed input, and path traversal handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/copyurl/copyurl_test.go -->
