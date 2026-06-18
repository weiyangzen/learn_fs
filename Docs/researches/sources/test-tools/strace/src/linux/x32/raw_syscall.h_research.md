# sources/test-tools/strace/src/linux/x32/raw_syscall.h

## Purpose
Reuses the x86_64 raw-syscall helper implementation for x32 by including `../x86_64/raw_syscall.h`.

## Important APIs, Types, And Functions
The included header defines guarded `raw_syscall_0(const kernel_ulong_t nr, kernel_ulong_t *err)` as an inline assembly `syscall` instruction wrapper. It writes `*err = 0`, places the syscall number in `rax`, returns the raw `rax` result, and clobbers `memory`, `cc`, `rcx`, and `r11`. It also defines the `raw_syscall_0` feature macro.

## Control Flow
This file has only preprocessor control flow: it delegates to the x86_64 header. The effective helper executes a zero-argument syscall directly and returns without libc errno translation. The caller is responsible for interpreting the raw return convention.

## State And Persistence
No persistent local state. The effective raw syscall can have whatever kernel-visible side effects the requested syscall number has, but this wrapper itself only mutates the caller-provided `err` storage and CPU registers involved in the syscall ABI.

## Dependencies And Integration Points
Depends on `sources/test-tools/strace/src/linux/x86_64/raw_syscall.h` and `kernel_types.h`. It is part of the architecture support included where strace needs minimal direct syscalls, typically for probing or helper operations that should avoid libc wrappers. Sharing the x86_64 implementation is consistent with x32 using the x86_64 `syscall` instruction and register calling convention.

## Risks
The x86_64 implementation exposes only zero-argument raw syscalls. It always clears `*err`, so callers must not expect errno-style reporting from this helper. If an x32-specific syscall numbering or ABI quirk applies to a caller, the shared x86_64 wrapper will not compensate; that logic has to live at the call site.

## Test Signals
Build tests should confirm the include guard prevents duplicate definitions. Runtime probes that use `raw_syscall_0` on x32 should return the same raw kernel results as equivalent x86_64 ABI calls for zero-argument syscall numbers. Assembly-sensitive tests should watch for register clobber correctness.

## Source-Read Signal
Reviewed the complete local file and the complete included x86_64 helper to characterize the effective API.
