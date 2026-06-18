# sources/test-tools/liburing/src/arch/x86/syscall.h

## sources/test-tools/liburing/src/arch/x86/syscall.h

Purpose: x86 raw syscall macro layer for x86_64 and i386 nolibc builds, with generic fallback when raw i386 is not enabled.

Important APIs/macros: x86_64 `__do_syscall0` through `__do_syscall6` using `syscall`, `rax/rdi/rsi/rdx/r10/r8/r9`; i386 nolibc variants using `int $0x80`, `eax/ebx/ecx/edx/esi/edi/ebp`; special six-argument i386 stack workaround for `%ebp`; includes `../syscall-defs.h`.

Control flow: preprocessor selects x86_64 raw syscalls, else i386 raw syscalls only under `CONFIG_NOLIBC`, else generic libc wrappers.

State and persistence: none.

Dependencies/integration: Linux x86 syscall ABIs, compiler inline asm constraints, and nolibc liburing internals.

Risks: i386 six-argument syscall workaround is delicate and documents a GCC bug avoidance. Raw asm clobber lists must remain correct. Return values are raw kernel negatives, not `errno`-translated.

Test signals: x86_64 and i686 CI compilation; nolibc runtime tests on supported x86 paths.
