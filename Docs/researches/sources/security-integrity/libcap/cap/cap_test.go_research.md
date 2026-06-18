<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/cap/cap_test.go -->
# sources/security-integrity/libcap/cap/cap_test.go

## Purpose
Unit tests for core Go capability set logic, text conversion, import/export encoding, IAB behavior, and function-launch state isolation.

## Important APIs, Types, And Functions
Tests `bitOf`, `allMask`, `Value.String`, `FromText`, `Set.String`, `Export`, `Import`, `IABFromText`, `IAB.String`, `IAB.Fill`, `IAB.SetVector`, `FuncLauncher`, `Prctl`, and `Prctlw`.

## Control Flow
The tests force max-bit/word values for mask checks, parse and stringify known text cases, repeatedly mutate sets and validate export/import/text round trips, parse and mutate IAB tuples, read PID 1 capabilities, and run a launcher callback that flips `PR_KEEP_CAPS` without leaking it back.

## State And Persistence Behavior
Most state is in-memory package data. `TestFuncLaunch` mutates process secure state through `Prctlw` but verifies launcher isolation restores the outer process state and then intentionally flips it for the next iteration.

## Dependencies And Integration Points
Exercises internals because tests are in package `cap`. Relies on `/proc` and prctl support for some cases and on the launcher support for the active Go toolchain.

## Risks And Edge Cases
The test modifies package globals and process securebits; defers restore for globals but process prctl state depends on test ordering. Environment without PID 1 status visibility can fail IAB tests.

## Test Signals
Signals are exact canonical text, stable binary export sizes, lossless import/export, IAB round trips, and no privileged-state leak from `FuncLauncher`.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/cap/cap_test.go -->
