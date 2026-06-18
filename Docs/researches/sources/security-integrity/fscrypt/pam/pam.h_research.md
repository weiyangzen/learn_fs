# sources/security-integrity/fscrypt/pam/pam.h

## Purpose
`pam.h` declares the C bridge functions and types shared between `pam.c` and cgo in `pam.go`.

## Important APIs, Types, and Functions
It declares `goConv`, `CleanupFunc`, `freeData`, `freeArray`, `copyIntoSecret`, `freeSecret`, and `infoMessage`.

## Control Flow
There is no implementation control flow in the header. It defines ABI signatures used by Go cgo declarations.

## State and Persistence
No state is stored here. The declarations govern PAM data cleanup and secret handling implemented in `pam.c`.

## Dependencies and Integration Points
Includes `<security/pam_appl.h>`. Used by both the C implementation and Go cgo block.

## Risks
Signature mismatches would cause build or runtime memory safety issues. The typo in comments (`CleaupFunc`) is harmless but present.

## Test Signals
Covered by successful cgo compilation and any PAM integration tests. There are no direct header tests.
