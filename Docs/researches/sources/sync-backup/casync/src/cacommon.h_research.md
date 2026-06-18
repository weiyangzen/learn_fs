# sources/sync-backup/casync/src/cacommon.h

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/casync/src/cacommon.h -->
## sources/sync-backup/casync/src/cacommon.h

Purpose: `cacommon.h` defines a shared iteration direction enum used by casync APIs that navigate ordered collections.

Important APIs and types: `CaIterate` contains `CA_ITERATE_CURRENT`, `CA_ITERATE_FIRST`, `CA_ITERATE_LAST`, `CA_ITERATE_NEXT`, `CA_ITERATE_PREVIOUS`, `_CA_ITERATE_MAX`, and `_CA_ITERATE_INVALID = -1`.

Control flow contract: callers can pass these enum values to functions that need relative or absolute iteration movement. `_CA_ITERATE_MAX` is a sentinel for bounds checking, and `_CA_ITERATE_INVALID` supports error/default initialization.

State and persistence: no state or persistence. This is a pure shared type header.

Dependencies and integration points: it has no includes and is safe to include broadly. It likely integrates with index, archive, or traversal code elsewhere in `src`.

Risks: because this header is small and generic, meaning depends entirely on consuming APIs. Callers should not persist enum numeric values across incompatible versions unless the protocol documents them.

Test signals: compile-time coverage comes from consumers. Unit tests for iterator consumers should exercise every enum value and invalid handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/casync/src/cacommon.h -->
