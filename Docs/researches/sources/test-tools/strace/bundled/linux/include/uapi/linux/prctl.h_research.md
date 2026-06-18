# sources/test-tools/strace/bundled/linux/include/uapi/linux/prctl.h

## Purpose

Defines command numbers and subflags for `prctl(2)`, covering process lifecycle, credentials, memory layout, security hardening, architecture-specific controls, and newer runtime knobs. strace uses it to name the first argument and decode command-specific remaining arguments.

## Important APIs, Types, and Dependencies

The header depends on `linux/types.h`. It exports classic commands for parent-death signals, dumpability, unaligned/FPU/endian controls, keepcaps, seccomp, capability bounding set, TSC, securebits, timerslack, perf enable/disable, memory corruption kill mode, `PR_SET_MM`, ptracer, child subreaper, no-new-privs, TID address, THP disable, ambient capabilities, SVE/SME vector length, speculation controls, pointer authentication, tagged address/MTE/RISC-V pointer masking, syscall user dispatch, core scheduling, MDWE, named anonymous VMAs, auxv fetch, memory merge, RISC-V vector and icache controls, PowerPC DEXCR, shadow-stack controls, timer restore ids, futex hash, rseq slice extension, and CFI controls. `struct prctl_mm_map` provides the complex `PR_SET_MM_MAP` payload.

## Control Flow, State, and Integration

There is no local code flow. Each constant selects a kernel operation on the current task, process, mm, credentials, architecture state, or security policy. Some settings persist across exec or can be locked; others are process-local, thread-local, or architecture-specific.

## Risks and Test Signals

Risks are command-specific argument interpretation, unsigned long flag width on 32-bit userspace, reserved command numbers that remain nonfunctional, and decode ambiguity for architecture-only controls. Test signals are syscall decoding tests for each command family, `struct prctl_mm_map` field output, named flag sets for speculation, SVE/SME, MTE, shadow-stack, rseq slice, and CFI, plus unknown command fallback.
