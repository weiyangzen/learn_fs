<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmdtest/cmdtest.go -->
# sources/user-network-fs/rclone/cmdtest/cmdtest.go

## Purpose

`cmdtest.go` provides a `main` entry point for end-to-end tests that execute rclone's real CLI inside the test binary.

## Important APIs, Types, and Functions

The file's `main` imports all backends and commands for side effects, calls `fsfile.Init`, initializes rclone's runtime with `cmd.Init`, sets `siginfo.SigInfoHandler` to dump goroutines, then invokes `cmd.Main`.

## Control Flow

`cmdtest_test.go` re-executes the test binary with `RCLONE_TEST_MAIN`; `TestMain` then calls this `main` so the child process behaves like the real rclone binary.

## State and Persistence Behavior

It creates normal rclone process-global state in the child process. No durable state is written here directly, though invoked commands may create configs or files.

## Dependencies and Integration Points

It integrates all command packages, all backends, fsfile initialization, signal handling, and rclone's CLI startup path.

## Risks and Test Signals

Risks are side-effect import drift and differences between test binary and production binary initialization. End-to-end tests should catch missing command/backend imports and initialization regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmdtest/cmdtest.go -->
