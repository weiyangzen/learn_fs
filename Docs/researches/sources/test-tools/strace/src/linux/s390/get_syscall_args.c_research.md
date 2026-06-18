<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/get_syscall_args.c -->
# sources/test-tools/strace/src/linux/s390/get_syscall_args.c

## Purpose

This file implements or selects a s390 32-bit architecture hook for strace. Local functions/macros are arch_get_syscall_args. `arch_get_syscall_args` copies up to six syscall arguments from ABI-defined argument registers into `tcp->u_arg`; compat paths zero-extend 32-bit register values.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `s390` strace backend. It has SHA-1 prefix `14c304fab4dc`, 23 lines, and 540 bytes. Key local interface signals: defines ARCH_REGSET; functions arch_get_syscall_args.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/s390`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register selection mistakes produce wrong syscall numbers, arguments, or errno state, which cascades into incorrect decoder selection and misleading traces. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Run syscall-entry/exit tests under ptrace, including failure returns, restart_syscall where applicable, syscall tampering, and compat personality switching. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390/get_syscall_args.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/get_syscall_args.c -->
