# sources/test-tools/syzkaller/pkg/fuzzer/fuzzer_test.go

## Purpose
This file provides an end-to-end fuzzer smoke test using syzkaller's test target and local RPC executor, plus a parallel benchmark for request generation and completion.

## Important APIs, Types, And Functions
`TestFuzz` builds a test executor with coverage instrumentation, creates a monitored corpus, constructs a fuzzer with one enabled syscall, runs `testFuzzer`, and asserts expected crashes and non-empty corpus/signal. `BenchmarkFuzzer` creates a full-call fuzzer and runs parallel `Next`/`Done` cycles using `emulateExec`. `emulateExec` derives deterministic per-call signal/cover from serialized program lines and syscall IDs.

`testFuzzer` implements `queue.Source` for `rpcserver.RunLocal`. Its `Next` delegates to `fuzzer.Next`, adds executor environment flags and output/error requests, and installs an `OnDone` hook. `OnDone` detects crash markers in executor output, tracks crash classes, logs progress, and cancels once iteration limit or success criteria are met. `checkGoroutineLeaks` scans runtime stacks for leaked fuzzer goroutines after context cancellation.

## Control Flow
The test starts a local RPC server with `MachineChecked` returning the `testFuzzer` source. Executor workers repeatedly call `Next`, execute requests, and invoke callbacks. The callback can mark results as crashed based on output and terminates the test by canceling context when all expected crashes and corpus/signal criteria are satisfied.

## State And Persistence Behavior
State is test-local: crash counters, iteration count, output buffer, temporary executor directory, monitored corpus, and an atomic finished flag. The finished flag avoids data races and late logging after the test ends.

## Dependencies And Integration Points
The test integrates `csource`, `rpcserver`, `vminfo`, `flatrpc`, `queue`, `corpus`, `prog`, `targets`, and `testutil`. It is the strongest signal that fuzzer queues, generated requests, local executor protocol, corpus saving, and crash handling work together.

## Risks
The test depends on target compiler availability and skips if the cross-compiler is broken. It has an iteration limit, so slow or unlucky fuzzing can fail even if the implementation is correct. Hints are not emulated in `OnDone`, leaving that path less covered by this integration test.

## Test Signals
Assertions require all expected crash classes, non-empty corpus, and non-empty signal. The benchmark checks for allocation/performance regressions in the hot fuzzer loop but does not assert behavioral outcomes beyond successful execution.
