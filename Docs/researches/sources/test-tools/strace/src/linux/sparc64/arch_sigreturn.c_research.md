<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/arch_sigreturn.c -->
# sources/test-tools/strace/src/linux/sparc64/arch_sigreturn.c

## Purpose

This file decodes the architecture-specific sigreturn frame for sparc64. It reads frame data from the stack pointer, prints the saved signal mask address or fields, and handles compat structure sizing where present. It reuses shared code through "../sparc/arch_sigreturn.c", "../sparc/arch_sigreturn.c" while redefining size/personality macros around the include where needed.

## Important APIs, Types, And Functions

This source is classified as `sigreturn` for the `sparc64` strace backend. It has SHA-1 prefix `65920b8efb3c`, 26 lines, and 663 bytes. Key local interface signals: includes "../sparc/arch_sigreturn.c", "../sparc/arch_sigreturn.c"; defines arch_sigreturn, SIZEOF_STRUCT_SPARC_STACKF, SIZEOF_STRUCT_PT_REGS, PERSONALITY_WORDSIZE, arch_sigreturn; functions arch_sigreturn.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

preprocessor includes: "../sparc/arch_sigreturn.c", "../sparc/arch_sigreturn.c". The integration point is strace's per-architecture Linux backend under `src/linux/sparc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Exercise signal-delivery and sigreturn traces and verify saved mask/frame addresses for native and compat tasks. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sparc64/arch_sigreturn.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sparc64/arch_sigreturn.c -->
