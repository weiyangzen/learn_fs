<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/arch_regs.c -->
# sources/test-tools/strace/src/linux/sparc/arch_regs.c

## Purpose

This file implements or selects a SPARC 32-bit architecture hook for strace. Local functions/macros are U_REG_G1, U_REG_O0, U_REG_O1, U_REG_FP, ARCH_REGS_FOR_GETREGS, ARCH_PC_REG, ARCH_SP_REG. The file binds the generic register-fetch path to concrete global register storage plus `ARCH_PC_REG` and `ARCH_SP_REG` macros used by shared code.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `sparc` strace backend. It has SHA-1 prefix `d9cb24a431fe`, 19 lines, and 523 bytes. Key local interface signals: defines U_REG_G1, U_REG_O0, U_REG_O1, U_REG_FP, ARCH_REGS_FOR_GETREGS, ARCH_PC_REG, ARCH_SP_REG.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/sparc`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc/arch_regs.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/arch_regs.c -->
