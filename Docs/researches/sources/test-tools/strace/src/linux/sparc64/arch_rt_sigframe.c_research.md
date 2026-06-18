<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/arch_rt_sigframe.c -->
# sources/test-tools/strace/src/linux/sparc64/arch_rt_sigframe.c

## Purpose

This source computes the runtime address of the sparc64 realtime signal frame from the tracee stack pointer, with ABI-specific stack-bias or compat handling where required. The SPARC64 variant applies the 2047-byte stack bias for native 64-bit frames and masks to 32 bits for compat personality 1.

## Important APIs, Types, And Functions

This source is classified as `rt-sigframe` for the `sparc64` strace backend. It has SHA-1 prefix `f8348e0b77d5`, 17 lines, and 334 bytes. Key local interface signals: defines STACK_BIAS.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/sparc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Structure layout drift or alignment mistakes can over/under-print register fields; the code mitigates this with size checks but depends on exact ABI offsets. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Exercise signal-delivery and sigreturn traces and verify saved mask/frame addresses for native and compat tasks. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc64/arch_rt_sigframe.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/arch_rt_sigframe.c -->
