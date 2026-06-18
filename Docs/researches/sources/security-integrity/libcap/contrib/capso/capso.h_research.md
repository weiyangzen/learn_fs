<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/capso/capso.h -->
# sources/security-integrity/libcap/contrib/capso/capso.h

## Purpose
Public header for the `capso` demo shared object.

## Important APIs, Types, And Functions
Declares `int bind80(const char *hostname);` with include guards.

## Control Flow
Header-only declaration; runtime behavior is in `capso.c`.

## State And Persistence Behavior
No state.

## Dependencies And Integration Points
Included by `bind.c` and `capso.c` consumers.

## Risks And Edge Cases
The API returns a raw file descriptor or negative error; callers must close successful descriptors.

## Test Signals
Signals are successful compilation and linkage against `capso.so`.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/capso/capso.h -->
