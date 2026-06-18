<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/set_error.c -->
# sources/test-tools/strace/src/linux/s390/set_error.c

## Purpose

This file implements or selects a s390 32-bit architecture hook for strace. Local functions/macros are arch_set_error, arch_set_success. The set-error/success hooks mutate the cached register set, update condition-code/error bits when the ABI needs them, and call `set_regs(tcp->pid)` to persist the change into the tracee.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `s390` strace backend. It has SHA-1 prefix `a93f4286d888`, 24 lines, and 419 bytes. Key local interface signals: defines ARCH_REGSET; functions arch_set_error, arch_set_success.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

It mutates the cached architecture register block and persists it into the stopped tracee with `set_regs(tcp->pid)`.

## Dependencies And Integration Points

strace architecture include/build system. The integration point is strace's per-architecture Linux backend under `src/linux/s390`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register tampering bugs can leave the tracee with inconsistent return values or condition-code bits, so failures are behavioral rather than cosmetic. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Run syscall-entry/exit tests under ptrace, including failure returns, restart_syscall where applicable, syscall tampering, and compat personality switching. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390/set_error.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/set_error.c -->
