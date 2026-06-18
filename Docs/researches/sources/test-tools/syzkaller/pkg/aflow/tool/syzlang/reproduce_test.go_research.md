# sources/test-tools/syzkaller/pkg/aflow/tool/syzlang/reproduce_test.go

## Purpose
Tests `reproduce` validation behavior without requiring VM execution.

## Important APIs, Types, and Functions
Uses private `reproduce`, `reproduceState{TargetOS: linux, TargetArch: amd64}`, `ReproduceArgs`, and testify assertions.

## Control Flow
Table cases cover empty program, a valid syscall, malformed syntax, and unknown syscall. Because VM state is absent, the valid case stops after parse validation.

## State and Persistence Behavior
No VM, cache, or filesystem state is used.

## Dependencies and Integration Points
Validates integration with `prog.GetTarget` and strict syz program deserialization.

## Risks and Test Signals
Strong parse-level signal but no coverage for VM execution, crash report handling, or cached coverage IDs.
