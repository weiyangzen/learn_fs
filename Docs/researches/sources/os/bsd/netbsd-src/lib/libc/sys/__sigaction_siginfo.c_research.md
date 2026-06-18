# File Research: sources/os/bsd/netbsd-src/lib/libc/sys/__sigaction_siginfo.c

## Purpose
Implements the libc compatibility entry point `__sigaction_siginfo`.

## Key Elements
Builds the signal trampoline symbol name from `__SIGTRAMP_SIGINFO_VERSION` and calls `__sigaction_sigtramp(sig, act, oact, trampoline, version)`.

## Dependencies
Uses `<signal.h>`, `extern.h`, `__sigaction_sigtramp`, and the architecture-provided `__sigtramp_siginfo_*` trampoline symbol.

## Behavior/Risks
This is a versioned ABI shim; comments state it should become plain `sigaction` at the next libc major bump. The trampoline version must match kernel/libc signal ABI expectations.
