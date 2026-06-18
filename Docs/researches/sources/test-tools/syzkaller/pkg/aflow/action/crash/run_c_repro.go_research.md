# sources/test-tools/syzkaller/pkg/aflow/action/crash/run_c_repro.go

## Purpose

`run_c_repro.go` defines the `RunCRepro` action, which runs a formatted C reproducer in the configured VM and optionally re-runs with strace when the first run does not crash.

## Important APIs, Types, and Functions

`RunCReproArgs` carries target, VM, kernel, formatted C repro, and strace fields. `RunCReproResult` reports reproduction status, console and strace output, primary and secondary crash reports, and boot/test error text. `RunCReproFunc` validates inputs, creates a temp workdir, builds `ReproduceArgs`, calls `RunTest`, and maps `RunTestResult` into action outputs.

## Control Flow

The function rejects empty C repros and empty target arch. It performs a first `RunTest` without strace and records console output, boot error, primary report, and other reports. If the first run neither crashes nor has a boot error and strace was requested with a binary path, it sets `NeedStrace`, reruns the same C repro, stores the second run output as `StraceOutput`, and merges any crash/test results from that run.

## State and Persistence Behavior

It uses `ctx.TempDir()` for VM run work artifacts and relies on the enclosing context to remove the temp directory. It does not use the persistent cache itself, so repeated C repro attempts are not memoized here.

## Dependencies and Integration Points

It is used by the `reproc` workflow after C generation and compilation. It depends on `RunTest` from `reproduce.go` for all VM behavior and on aflow action registration.

## Risks and Edge Cases

`RunCReproArgs.NeedStrace` is only honored when `StraceBin` is non-empty and the first run is clean. The initial `ReproduceArgs` does not copy `NeedStrace`, which is intentional for run 1 but important to preserve. Errors from the second run return the partial first-run result plus the error. Other reports can contain reports from both runs.

## Test Signals

No direct unit test is present in this file set. It is exercised through C-repro workflow integration and depends heavily on `RunTest` behavior.
