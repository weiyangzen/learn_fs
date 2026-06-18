# sources/test-tools/syzkaller/pkg/aflow/action/crash/reproduce_test.go

## Purpose

`reproduce_test.go` unit-tests crash result aggregation without booting VMs.

## Important APIs, Types, and Functions

`TestAggregateTestResults` constructs `instance.EnvTestResult` slices containing `instance.CrashError`, `instance.TestError`, and successful runs, then calls `aggregateTestResults` with a dummy linux/amd64 reporter.

## Control Flow

Each table case feeds synthetic run results into the aggregator. Assertions check that the selected primary report has the expected title/report body, that boot errors are recorded when no crash wins, and that all-ok inputs produce neither report nor boot error.

## State and Persistence Behavior

The test uses no aflow cache or VM state. The only constructed state is a `report.Reporter` configured with linux/amd64 derived target fields.

## Dependencies and Integration Points

It depends on `pkg/instance`, `pkg/mgrconfig`, `pkg/report`, and `testify/require`. It verifies the contract expected by `RunTest` after `instance.CollectRuns`.

## Risks and Edge Cases

The test does not cover coverage symbolization, fault injection extraction, raw console output, or tie-breaking for equal crash counts with different titles. It also bypasses JSON VM config and manager setup.

## Test Signals

The cases provide strong regression coverage for selecting the most frequent crash and not letting boot errors override crashes.
