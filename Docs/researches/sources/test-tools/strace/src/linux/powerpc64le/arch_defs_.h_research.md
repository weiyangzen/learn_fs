<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/arch_defs_.h -->
# sources/test-tools/strace/src/linux/powerpc64le/arch_defs_.h

## Purpose

This architecture definition header advertises strace compile-time capabilities for the powerpc64le backend: HAVE_ARCH_OLD_SELECT, PERSONALITY0_AUDIT_ARCH. The `PERSONALITY*_AUDIT_ARCH` macros are the bridge from seccomp/audit syscall-info records to strace personality selection.

## Important APIs, Types, And Functions

This source is classified as `arch-defs` for the `powerpc64le` strace backend. It has SHA-1 prefix `a3c9b9a450b2`, 9 lines, and 220 bytes. Key local interface signals: defines HAVE_ARCH_OLD_SELECT, PERSONALITY0_AUDIT_ARCH.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

Linux audit architecture constants. The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64le`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64le/arch_defs_.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64le/arch_defs_.h -->
