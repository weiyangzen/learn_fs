<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/set_scno.c -->
# sources/test-tools/strace/src/linux/s390x/set_scno.c

## Purpose

This file implements or selects a s390 64-bit architecture hook for strace. Local functions/macros are arch_set_scno.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `s390x` strace backend. It has SHA-1 prefix `f437ef6a9105`, 27 lines, and 580 bytes. Key local interface signals: includes "../s390/set_scno.c", "../s390/set_scno.c"; defines arch_set_scno, ARCH_REGSET, arch_set_scno, ARCH_REGSET; functions arch_set_scno.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

preprocessor includes: "../s390/set_scno.c", "../s390/set_scno.c". The integration point is strace's per-architecture Linux backend under `src/linux/s390x`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register tampering bugs can leave the tracee with inconsistent return values or condition-code bits, so failures are behavioral rather than cosmetic. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390x/set_scno.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/set_scno.c -->
