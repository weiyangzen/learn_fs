# sources/test-tools/syzkaller/prog/export_test.go

Purpose: exposes selected internals and common target/random helpers for package tests.

Important APIs/types/functions: `init` sets `debug = true`; exported aliases `CalcChecksumsCall`, `InitTest`, and `initTargetTest`; helpers `initRandomTargetTest`, `initTest`, `testEachTarget`, `testEachTargetRandom`, `skipTargetRace`, and `initBench`.

Control flow and state: test initialization enables debug validation globally. Target iteration runs subtests in parallel, with race-mode filtering to keep CI runtime manageable. Random helpers provide deterministic testutil sources and iteration counts. `initBench` temporarily disables debug and returns a cleanup closure.

Dependencies and integration: imports `pkg/testutil`, target loading, and Go testing/benchmark APIs. Used throughout this subset's tests for target setup, randomness, checksum export, and benchmark setup.

Risks: global `debug` mutation affects all package tests and must be restored in benchmarks. Parallel target tests require helpers to avoid shared mutable target state bugs. Race-mode filtering may reduce architecture coverage.

Test signals: this file is infrastructure rather than a test subject; failures in many tests would expose broken helper behavior.
