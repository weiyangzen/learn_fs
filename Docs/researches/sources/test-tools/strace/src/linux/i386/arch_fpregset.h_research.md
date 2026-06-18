# sources/test-tools/strace/src/linux/i386/arch_fpregset.h

Purpose: declares the `i386` regset struct shape and enables the matching decoder.

Important APIs/types/functions: STRACE_ARCH_FPREGSET_H, HAVE_ARCH_FPREGSET; notable register references include none in this file.

Control flow: no executable flow; the typedef and `HAVE_ARCH_*` macro let generic code compile the architecture decoder.

State/persistence behavior: operates on transient tracee/register/memory snapshots or compile-time metadata; persistent program state is not introduced here.

Dependencies/integration: Depends on architecture kernel user register types or locally declared field order; includes no external header in this file.

Risks/test signals: typedef drift from kernel ABI breaks register dumps; compile with current headers and run ptrace regset decoding tests.

Source-read signal: reviewed complete local file (24 lines).
