# sources/user-network-fs/mergerfs/src/policy_rv.hpp

## Purpose
Defines `PolicyRV`, a structured return container for policy operations that need to report both successes and per-branch errors.

## Important APIs, Types, and Functions
`PolicyRV::RV` stores `rv`, `basepath`, and `fullpath`. The parent struct has `std::vector<RV> successes` and `errors`, plus convenience predicates `empty()`, `success()`, and `error()`.

## Control Flow
There is no active control flow beyond predicate evaluation. Callers populate success and error vectors while iterating branches, then inspect aggregate status.

## State and Persistence Behavior
The struct is caller-owned transient state. It does not persist data, but it can describe which underlying branch paths were affected by filesystem operations.

## Dependencies and Integration Points
It depends on `string` and `vector` and is suited for policy or FUSE helpers that need multi-branch result reporting.

## Risks and Edge Cases
`success()` and `error()` are not mutually exclusive; a partial operation can have both successes and errors. Callers must decide precedence and rollback behavior.

## Test Signals
Unit tests should cover empty, success-only, error-only, and mixed states, plus consumers that translate partial results into errno values.
