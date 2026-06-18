# sources/test-tools/strace/src/set_tid_address.c

Purpose: tiny decoder for `set_tid_address`.

Important APIs/types/functions: `SYS_FUNC(set_tid_address)`, `printaddr`, and return flags `RVAL_DECODED | RVAL_TID`.

Control flow: prints the `tidptr` address and marks the syscall as decoded, with return value interpreted as a thread id.

State and persistence behavior: stateless; it does not dereference the clear-child-tid pointer.

Dependencies and integration points: integrated via syscall tables and core return-value formatting for TIDs.

Risks: low risk; dereferencing would be wrong here because the pointer is a kernel futex/clear-child-tid address rather than a simple input value.

Test signals: verify pointer formatting and TID return annotation.
