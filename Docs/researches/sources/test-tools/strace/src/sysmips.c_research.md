# sources/test-tools/strace/src/sysmips.c

Purpose: MIPS-only decoder for `sysmips`.

Important APIs/types/functions: `SYS_FUNC(sysmips)`, `sysmips_operations`, `MIPS_ATOMIC_SET`, and `MIPS_FIXADE`.

Control flow: compiled only under `MIPS`. Prints command name, then special-cases `MIPS_ATOMIC_SET` as address plus hex value and `MIPS_FIXADE` as one hex argument; otherwise prints three hex arguments.

State and persistence behavior: stateless.

Dependencies and integration points: depends on MIPS kernel headers and generated operation xlats; selected by MIPS syscall tables.

Risks: command-specific argument schemas are sparse; unknown commands are raw hex. Non-MIPS builds omit the decoder body.

Test signals: MIPS build, known operations, unknown operation, and syscall table compile on non-MIPS.
