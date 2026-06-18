# sources/test-tools/syzkaller/pkg/vminfo/vminfo_test.go

## Purpose

This file tests the VM-info checker across host machine-info collection and non-Linux syscall checking.

## Important APIs, Types, And Functions

`TestHostMachineInfo` reads host-required files and runs `MachineInfo`. `TestSyscalls` iterates all non-Linux targets and verifies synthetic successful execution enables every syscall. Helpers include `allFeatures`, `createSuccessfulResults`, `hostChecker`, `testConfig`, `readFiles`, and `readFile`.

## Control Flow, State, Dependencies, And Integration

`createSuccessfulResults` drives the checker as a `queue.Source`, responding to program and glob requests, and panics if more than 1000 requests are generated. Host checks read real files where available. Target configs use all non-disabled syscalls and all features.

## Risks And Test Signals

The request-count guard protects deduplication and catches accidental explosion in generated test programs. Host tests are environment-dependent and log read errors rather than failing on missing files. Generic syscall tests do not validate real OS availability because all executor results are synthetic successes.
