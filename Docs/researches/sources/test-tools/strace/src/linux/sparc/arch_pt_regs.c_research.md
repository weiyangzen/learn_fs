<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/arch_pt_regs.c -->
# sources/test-tools/strace/src/linux/sparc/arch_pt_regs.c

## Purpose

This file implements or selects a SPARC 32-bit architecture hook for strace. Local functions/macros are arch_decode_pt_regs. The pt_regs decoder prints kernel `struct pt_regs` fields for ptrace or signal-frame contexts, with compat guards on bi-ABI targets.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `sparc` strace backend. It has SHA-1 prefix `93452eba6b5c`, 38 lines, and 702 bytes. Key local interface signals: functions arch_decode_pt_regs.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace structured printing macros. The integration point is strace's per-architecture Linux backend under `src/linux/sparc`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Structure layout drift or alignment mistakes can over/under-print register fields; the code mitigates this with size checks but depends on exact ABI offsets. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Decode NT_PRSTATUS/pt_regs samples with full, truncated, and oversized sizes to validate graceful printing. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc/arch_pt_regs.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc/arch_pt_regs.c -->
