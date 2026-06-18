# sources/test-tools/syzkaller/syz-cluster/pkg/api/api.go

## Purpose
Shared wire-contract schema for syz-cluster workflow steps, controller APIs, reporter APIs, and service conversions.

## Important APIs, Types, and Functions
Defines TriageResult, TestTarget, RetestTask, FuzzConfig, Tree, KernelFuzzConfig, BuildRequest/BuildResult/Build, SessionTest, SessionTestStep, RawFinding, Series/Patch, SessionReport, Finding, Job, SessionInfo, and string constants for focus areas, statuses, report types, and job types.

## Control Flow
No main algorithm; methods are schema helpers such as Series.PatchBodies. Control flow is driven by downstream clients/services that serialize these structs.

## State and Persistence
No direct persistence, but JSON/YAML tags and byte fields are the cross-process and Spanner/blob handoff contract.

## Dependencies and Integration Points
Depends on Go net/http/json helpers and is integrated by controller/reporter servers plus workflow clients.

## Risks and Edge Cases
Risks include wire-contract drift, weak validation of string statuses, memory buffering for large payloads, and coarse HTTP error mapping.

## Test Signals
Covered indirectly by controller, reporter, retest, fuzzconfig, and report integration tests.
