# sources/test-tools/strace/src/syscall.h

Purpose: top-level syscall decoder declaration header.

Important APIs/types/functions: includes `syscall_dummy.h` and `sys_func.h`; conditionally declares UID16 syscall printers such as `chown16`, `getuid16`, `setresuid16`, and related group/uid functions.

Control flow: compile-time `HAVE_ARCH_UID16_SYSCALLS` controls whether legacy 16-bit UID function prototypes are exposed.

State and persistence behavior: no state.

Dependencies and integration points: included where generated syscall tables need printer prototypes and dummy aliases.

Risks: missing prototypes can become build failures when generated tables reference legacy functions; overbroad dummy aliases can hide missing real decoders.

Test signals: builds with and without `HAVE_ARCH_UID16_SYSCALLS` and generated tables referencing UID16 calls.
