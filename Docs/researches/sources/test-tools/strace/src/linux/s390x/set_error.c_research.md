<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/set_error.c -->
# sources/test-tools/strace/src/linux/s390x/set_error.c

## Purpose

This file implements or selects a s390 64-bit architecture hook for strace. Local functions/macros are arch_set_error, arch_set_success. The set-error/success hooks mutate the cached register set, update condition-code/error bits when the ABI needs them, and call `set_regs(tcp->pid)` to persist the change into the tracee.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `s390x` strace backend. It has SHA-1 prefix `0824531340b0`, 40 lines, and 837 bytes. Key local interface signals: includes "../s390/set_error.c", "../s390/set_error.c"; defines arch_set_error, arch_set_success, ARCH_REGSET, arch_set_error, arch_set_success, ARCH_REGSET; functions arch_set_error, arch_set_success.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

preprocessor includes: "../s390/set_error.c", "../s390/set_error.c". The integration point is strace's per-architecture Linux backend under `src/linux/s390x`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register tampering bugs can leave the tracee with inconsistent return values or condition-code bits, so failures are behavioral rather than cosmetic. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Run syscall-entry/exit tests under ptrace, including failure returns, restart_syscall where applicable, syscall tampering, and compat personality switching. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390x/set_error.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390x/set_error.c -->
