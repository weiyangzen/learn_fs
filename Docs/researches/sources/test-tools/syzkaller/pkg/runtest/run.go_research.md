# sources/test-tools/syzkaller/pkg/runtest/run.go

## Purpose

`run.go` is the syzkaller program runtime-test driver. It generates syz-executor and C-source test requests across sandboxes, threading, repetition, and coverage modes, submits them to a queue executor, and checks observed call results against expectations encoded in test program comments.

## Important APIs, Types, And Functions

`Context` is the main driver configuration: test directory, target, supported features, enabled calls by sandbox, logging, retry count, verbosity, debug flag, and filename filter. `Init`, `Run`, and `Next` form the public workflow. Private helpers include `generatePrograms`, `progFileList`, `generateFile`, `parseProg`, `produceTest`, `createTest`, `submit`, `createSyzTest`, `createCTest`, `checkResult`, `checkCallResult`, `checkCallStatus`, `checkCallCoverage`, and `parseBinOutput`.

## Control Flow

`Run` calls `generatePrograms`, waits for created requests, reports per-test status, removes generated binaries, and fails if any test failed. `generateFile` parses a seed/test file, expands it over enabled sandboxes, threaded/unthreaded modes, repeat counts, and coverage modes, creates syz or C requests, and skips/breaks unsupported combinations. C requests build source asynchronously behind a `GOMAXPROCS` semaphore, then become binary queue requests. Completion goes through `onDone`, which tolerates flaky timing by rerunning until successes outnumber failures or retry budget is exhausted.

## State, Dependencies, Integration, And Risks

State includes generated request list, dynamic orderer executors, build semaphore, temporary binaries, per-request pass/fail counts, expected `flatrpc.ProgInfo`, and C repeat counts. Dependencies are `csource`, `flatrpc`, `queue`, `manager.ParseSeedWithRequirements`, `prog`, and `targets`. Integration points include `tools/syz-runtest`, `pkg/runtest` tests, executor RPC, csource generation, and sys/*/test files. Risks include combinatorial test expansion, flaky timing heuristics, platform-specific errno/comment mapping, missing coverage for pseudo syscalls, C output parser fragility, and broken non-fork repeat modes.

## Test Signals

`run_test.go` validates parsing, feature expectations, coverage/signal/comparison handling, and local executor execution. `executor_test.go` covers executor built-ins and extension behavior.
