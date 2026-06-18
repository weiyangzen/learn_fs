# sources/test-tools/liburing/src/arch/aarch64/syscall.h

## sources/test-tools/liburing/src/arch/aarch64/syscall.h

Purpose: AArch64 raw syscall macro layer for nolibc/liburing internals, falling back to generic libc wrappers when not compiling for AArch64.

Important APIs/macros: `__do_syscall0` through `__do_syscall6`, using registers `x8` for syscall number and `x0`-`x5` for args, issuing `svc 0`; includes `../syscall-defs.h`.

Control flow: preprocessor selects native macros under `__aarch64__`, otherwise includes generic syscall implementation. Syscall wrappers in `syscall-defs.h` build on these macros.

State and persistence: none.

Dependencies/integration: depends on Linux AArch64 syscall ABI, syscall numbers, and compiler support for register variables/inline asm.

Risks: raw syscalls return negative errno values directly and callers must interpret consistently. Inline asm constraints must remain ABI-correct across compilers. Non-AArch64 cross include silently uses generic wrappers.

Test signals: aarch64 CI compilation and nolibc runtime tests where available.
