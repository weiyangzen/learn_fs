# sources/test-tools/syzkaller/syz-cluster/pkg/retest/retest.go

## Purpose
Runner for retesting reproducers on base and patched kernels.

## Important APIs, Types, and Functions
Runner, Run, retestFinding, testOnEnv, testResult, uploadStep.

## Control Flow
Fetches original finding, tests optional base and patched envs, uploads steps, and uploads a new finding only for patched-only crashes.

## State and Persistence
Persists results through controller API calls to SessionTestSteps and Findings.

## Dependencies and Integration Points
Integrates syzkaller instance.Env, controller API, findings, test steps, and retest workflow tasks.

## Risks and Edge Cases
Risks include partial per-finding failures returning nil from Run, nil environment assumptions, and base-crash suppression semantics.

## Test Signals
retest_test.go covers major pass/crash/error scenarios with mock environments.
