<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/ptracetab.h -->
# sources/security-integrity/audit-userspace/auparse/ptracetab.h

## Purpose
Maps `ptrace` request numbers to symbolic names.

## Important APIs, types, and functions
The `_S` table includes classic ptrace operations plus extended `0x4200+` requests such as set options, get/set siginfo, regsets, seize, interrupt, seccomp filter/metadata, syscall info, rseq config, and syscall user dispatch config.

## Control flow
Generated `ptrace_i2s` is called by `interpret.c:print_ptrace` for `ptrace` syscall argument `a0`.

## State and persistence behavior
Static lookup data only.

## Dependencies and integration points
Tracks Linux ptrace and x86 ptrace ABI headers. Integrated with syscall argument interpretation.

## Risks and test signals
Risks are arch-specific request values and new kernel requests. Tests should cover classic and extended requests plus unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/ptracetab.h -->
