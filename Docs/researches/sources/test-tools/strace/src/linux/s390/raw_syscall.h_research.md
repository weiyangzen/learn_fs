<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/raw_syscall.h -->
# sources/test-tools/strace/src/linux/s390/raw_syscall.h

## Purpose

This header defines an inline `raw_syscall_0` helper for s390 bootstrap/probing paths. It binds syscall-number and return registers with inline assembly and reports a separate error flag pointer to the generic raw syscall caller. The implementation uses an SVC-style trap sequence for the architecture.

## Important APIs, Types, And Functions

This source is classified as `raw-syscall` for the `s390` strace backend. It has SHA-1 prefix `239b5e948a14`, 29 lines, and 607 bytes. Key local interface signals: includes "kernel_types.h"; defines STRACE_RAW_SYSCALL_H, raw_syscall_0; functions raw_syscall_0.

## Control Flow

Callers pass a syscall number to `raw_syscall_0`; inline assembly loads the ABI syscall register, enters the kernel, records whether an error occurred, and returns the raw result without using libc wrappers.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

preprocessor includes: "kernel_types.h". The integration point is strace's per-architecture Linux backend under `src/linux/s390`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

The main risk is architecture ABI drift: these small files encode register names, audit constants, and feature macros that must match kernel and libc headers. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Compile and execute raw-syscall smoke tests for a harmless syscall such as getpid or gettid, verifying raw return and error reporting. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/s390/raw_syscall.h_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/s390/raw_syscall.h -->
