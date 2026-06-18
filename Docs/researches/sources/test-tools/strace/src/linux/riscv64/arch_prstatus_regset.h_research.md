<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/riscv64/arch_prstatus_regset.h -->
# sources/test-tools/strace/src/linux/riscv64/arch_prstatus_regset.h

## Purpose

This header defines the type alias used to decode NT_PRSTATUS register-set payloads for riscv64 and sets `HAVE_ARCH_PRSTATUS_REGSET`.

## Important APIs, Types, And Functions

This source is classified as `prstatus-regset` for the `riscv64` strace backend. It has SHA-1 prefix `702c242cc2cd`, 15 lines, and 343 bytes. Key local interface signals: defines STRACE_ARCH_PRSTATUS_REGSET_H, HAVE_ARCH_PRSTATUS_REGSET.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/riscv64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Structure layout drift or alignment mistakes can over/under-print register fields; the code mitigates this with size checks but depends on exact ABI offsets. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Decode NT_PRSTATUS/pt_regs samples with full, truncated, and oversized sizes to validate graceful printing. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/riscv64/arch_prstatus_regset.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/riscv64/arch_prstatus_regset.h -->
