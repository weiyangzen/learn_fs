# sources/storage-engines/foundationdb/flow/include/flow/GetSourceVersion.h

## Purpose
`GetSourceVersion.h` declares the build/source version accessor used to report the FoundationDB source revision.

## Important APIs, Types, And Functions
The sole API is `const char* getSourceVersion()`.

## Control Flow
There is no inline control flow. The implementation returns a C string supplied by generated or build-linked version code.

## State And Persistence Behavior
The header owns no state. The returned pointer is expected to refer to static or otherwise stable build metadata.

## Dependencies And Integration Points
It is included by logging, diagnostics, command-line/version reporting, and support tooling that needs the source version without depending on build-system internals.

## Risks And Edge Cases
If the generated implementation is missing or stale, binaries can report incorrect source metadata. Callers should treat the returned pointer as read-only.

## Test Signals
Build/link tests, version command output, generated version-file checks, and packaging smoke tests validate this header's contract.
