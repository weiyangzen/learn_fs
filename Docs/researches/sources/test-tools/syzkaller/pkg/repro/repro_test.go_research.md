# sources/test-tools/syzkaller/pkg/repro/repro_test.go

## Purpose

This file tests the reproducer engine using fake executor behavior so the extraction, minimization, reliability, and crash-priority logic can be validated without real VMs.

## Important APIs, Types, And Control Flow

`initTest`, `testExecInterface`, `runTestRepro`, `fakeCrashResult`, and `testExecRunner` build a Linux/amd64 test environment and simulate crashes from serialized programs. `TestBisect` fuzzes `bisectProgs` with random guilty entries. `TestSimplifies` recursively verifies all C option simplification combinations remain valid. The plain repro, VM error, too-many-errors, concatenation, flaky, broken-compiler, and lost-connection tests drive `runInner` end to end.

## State, Dependencies, Risks, And Test Signals

Tests use `testutil.RandSource`, real `prog` target parsing, real reporter construction, and fake `instance.RunResult` values. They validate retry limits, minimum reliability behavior, title filtering, and C-repro skipping. The suite does not execute real generated C or real VM pools; integration with `poolWrapper` is covered elsewhere. Flaky probabilistic tests have thresholds rather than exact outcomes, so random seed quality and short-mode iteration counts matter.
