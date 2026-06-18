<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/arch_get_personality.c -->
# sources/test-tools/strace/src/linux/powerpc64/arch_get_personality.c

## Purpose

This file implements or selects a PowerPC 64-bit architecture hook for strace. Local functions/macros are get_personality_from_syscall_info. `get_personality_from_syscall_info` maps `PTRACE_GET_SYSCALL_INFO` audit architecture records to the compat personality for bi-ABI tracing.

## Important APIs, Types, And Functions

This source is classified as `arch-code` for the `powerpc64` strace backend. It has SHA-1 prefix `50636b19be42`, 13 lines, and 303 bytes. Key local interface signals: functions get_personality_from_syscall_info.

## Control Flow

The file participates in strace architecture hook dispatch: shared tracing code fetches registers, calls these static hooks through include-time wiring, and uses the resulting `struct tcb` fields for syscall decode, tampering, or signal-frame printing.

## State And Persistence Behavior

Mutable state lives outside this file in the per-tracee `struct tcb`, the architecture register cache, ptrace regsets, and tracee memory reached by `umoven_or_printaddr`; this file does not write durable storage.

## Dependencies And Integration Points

Linux ptrace regset APIs Linux audit architecture constants. The integration point is strace's per-architecture Linux backend under `src/linux/powerpc64`, where these files are pulled into common syscall tracing, register access, ioctl decoding, or signal-frame code by the build and include structure.

## Risks

Register selection mistakes produce wrong syscall numbers, arguments, or errno state, which cascades into incorrect decoder selection and misleading traces. Also watch for host/tracee word-size confusion, because many of these files are compiled on one host while describing another ABI's register and structure layout.

## Test Signals

Build strace for the target architecture or cross target with this file included. Non-empty generated research output for this file should be reconciled to `Docs/researches/sources/test-tools/strace/src/linux/powerpc64/arch_get_personality.c_research.md`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/linux/powerpc64/arch_get_personality.c -->
