<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh64/get_error.c -->
# sources/test-tools/strace/src/linux/sh64/get_error.c

## Purpose

This file implements or selects a SuperH 64-bit architecture hook for strace. Local functions/macros are arch_get_error. `arch_get_error` interprets the architecture error convention and fills `tcp->u_rval`/`tcp->u_error`, using negated errno helpers or condition-code bits as appropriate.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `sh64` strace backend. It has SHA-1 prefix `428b426ef9d6`, 19 lines, and 395 bytes. Key local interface signals: includes "negated_errno.h"; functions arch_get_error.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

preprocessor includes: "negated_errno.h" strace `negated_errno.h` helpers. The integration point is strace's per-architecture Linux backend under `src/linux/sh64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register selection mistakes produce wrong syscall numbers, arguments, or errno state, which cascades into incorrect decoder selection and misleading traces. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Run syscall-entry/exit tests under ptrace, including failure returns, restart_syscall where applicable, syscall tampering, and compat personality switching. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/sh64/get_error.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/sh64/get_error.c -->
