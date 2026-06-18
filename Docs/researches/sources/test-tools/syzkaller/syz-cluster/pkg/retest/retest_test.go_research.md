# sources/test-tools/syzkaller/syz-cluster/pkg/retest/retest_test.go

## Purpose
Retest runner scenario tests with mocked instance.Env.

## Important APIs, Types, and Functions
mockEnv, runTest, TestParams, TestRetestScenarios.

## Control Flow
Builds original and retest sessions, runs Runner, then verifies findings and step statuses.

## State and Persistence
Uses transient controller API, Spanner, and local blob storage.

## Dependencies and Integration Points
Integrates syzkaller instance.Env, controller API, findings, test steps, and retest workflow tasks.

## Risks and Edge Cases
Risks include partial per-finding failures returning nil from Run, nil environment assumptions, and base-crash suppression semantics.

## Test Signals
retest_test.go covers major pass/crash/error scenarios with mock environments.
