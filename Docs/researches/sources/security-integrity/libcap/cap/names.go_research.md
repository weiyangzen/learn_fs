<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/cap/names.go -->
# sources/security-integrity/libcap/cap/names.go

## Purpose
Generated Linux capability name table for the Go package.

## Important APIs, Types, And Functions
Defines `NamedCount`, constants from `CHOWN` through `CHECKPOINT_RESTORE`, and maps `names map[Value]string` and `bits map[string]Value`.

## Control Flow
No runtime control flow beyond map lookups by `Value.String` and `FromName`.

## State And Persistence Behavior
Static generated data only. Runtime `MaxBits` may exceed `NamedCount`, in which case numeric names are used for newer kernel capabilities.

## Dependencies And Integration Points
Generated from Linux UAPI capability definitions by libcap's Go builder. Used by text conversion, IAB parsing, examples, and documentation.

## Risks And Edge Cases
The table can lag newer kernels. Typos in generated descriptions or names would affect text parse/string compatibility with libcap.

## Test Signals
Signals are `FromName` examples, `Value.String` tests, and text parser round trips.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/cap/names.go -->
