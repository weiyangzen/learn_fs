<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/cap/cap_examples_test.go -->
# sources/security-integrity/libcap/cap/cap_examples_test.go

## Purpose
Testable examples for the public Go `cap` API. They serve both as documentation and as `go test` output checks for stable text/export behavior.

## Important APIs, Types, And Functions
Examples cover `Set.Fill`, `GetProc`, `NewSet`, `MaxBits`, `IABGetProc`, `NewIAB`, `Set.Export`, `Import`, `SetUID`, `FromText`, and `FromName`.

## Control Flow
Each example constructs or reads capability state, performs a small operation, and prints canonical output where deterministic. Privilege-dependent examples print informative runtime-dependent messages without fixed output.

## State And Persistence Behavior
Most examples are read-only or local `Set` transformations. `ExampleSetUID` can change the process UID if the process has permitted `SETUID`, so it is intentionally guarded by a capability check.

## Dependencies And Integration Points
Imports the public package path `kernel.org/pub/linux/libs/security/libcap/cap` and demonstrates consumer-facing use rather than internal package access.

## Risks And Edge Cases
Runtime-dependent examples do not assert output. `SetUID` is security-sensitive and intentionally exits early without permission.

## Test Signals
Signals are exact output for deterministic examples: empty sets, export bytes, import text, text equivalence, and name lookup.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/cap/cap_examples_test.go -->
