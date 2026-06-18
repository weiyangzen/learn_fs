<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/arch_prstatus_regset.c -->
# sources/test-tools/strace/src/linux/sparc64/arch_prstatus_regset.c

## Purpose

This decoder prints NT_PRSTATUS register-set payloads for sparc64. It bounds reads to `MIN(sizeof(regs), size)`, rejects misaligned or zero sizes, and prints only fields present in the fetched prefix. When the kernel supplies a larger blob than the known structure, it emits a more-data marker instead of over-reading unknown layout.

## Important APIs, Types, And Functions

This source is classified as `prstatus-regset` for the `sparc64` strace backend. It has SHA-1 prefix `6cd69d2dfce6`, 72 lines, and 2013 bytes. Key local interface signals: includes "../sparc/arch_prstatus_regset.c"; functions arch_decode_prstatus_regset.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

preprocessor includes: "../sparc/arch_prstatus_regset.c" strace structured printing macros tracee-memory readers. The integration point is strace's per-architecture Linux backend under `src/linux/sparc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Structure layout drift or alignment mistakes can over/under-print register fields; the code mitigates this with size checks but depends on exact ABI offsets. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Decode NT_PRSTATUS/pt_regs samples with full, truncated, and oversized sizes to validate graceful printing. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc64/arch_prstatus_regset.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/arch_prstatus_regset.c -->
