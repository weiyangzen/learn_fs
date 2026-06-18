# sources/test-tools/syzkaller/pkg/runtest/executor_test.go

## Purpose

This file runs executor-specific integration tests from Go, including built-in executor unit tests, zlib comparison behavior, and extension-hook behavior.

## Important APIs, Types, And Control Flow

`qemuBinary` maps Go arch names to qemu-user binaries for cross-arch execution. `handleCrossArchError` fails on CI or executor assertions but skips local cross-arch environment problems. `TestExecutor` builds each host-OS executor target and runs its `test` subcommand natively or under qemu. `TestZlib` builds the test executor, starts a local RPC server, sends random compressed/uncompressed image comparisons through `syz_compare_zlib`, and expects zero errno. `TestExecutorCommonExt` builds with `-DSYZ_TEST_COMMON_EXT_EXAMPLE=1` and checks that the common extension hook initialized memory visible to `syz_compare`.

## State, Dependencies, Risks, And Test Signals

Tests create temp dirs, executor binaries, local RPC servers, queue requests, random mount images, and optional qemu subprocesses. Dependencies include `csource`, `queue`, `image`, `osutil`, `testutil`, targets, and `startRPCServer` from `run_test.go`. Risks include qemu availability, cross-compiler availability, CI/local behavior differences, and subprocess cleanup. Passing tests prove executor built-ins, zlib helpers, and common extension setup work through the same RPC execution path used by fuzzing.
