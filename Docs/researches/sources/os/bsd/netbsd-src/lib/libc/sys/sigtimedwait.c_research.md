# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/sigtimedwait.c

## Purpose
Wraps the internal signal wait syscall to protect the caller's timeout object.

## Key Elements
Copies a non-null `timeout` into a local `timespec` and passes that to `__sigtimedwait`; passes `NULL` otherwise.

## Dependencies
Uses `<signal.h>`, `<time.h>`, and internal `__sigtimedwait`.

## Behavior/Risks
The copy allows the syscall path to modify the timeout without mutating user-visible const input.
