<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/arch_pt_regs64.h -->
# sources/test-tools/strace/src/linux/powerpc64/arch_pt_regs64.h

## Purpose

This file implements or selects a PowerPC 64-bit architecture hook for strace. Local functions/macros are STRACE_ARCH_PT_REGS64_H. The pt_regs decoder prints kernel `struct pt_regs` fields for ptrace or signal-frame contexts, with compat guards on bi-ABI targets.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `powerpc64` strace backend. It has SHA-1 prefix `c282e6b088f7`, 13 lines, and 272 bytes. Key local interface signals: defines STRACE_ARCH_PT_REGS64_H.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Structure layout drift or alignment mistakes can over/under-print register fields; the code mitigates this with size checks but depends on exact ABI offsets. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Decode NT_PRSTATUS/pt_regs samples with full, truncated, and oversized sizes to validate graceful printing. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64/arch_pt_regs64.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/arch_pt_regs64.h -->
