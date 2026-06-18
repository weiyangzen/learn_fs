<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/signaltab.h -->
# sources/security-integrity/audit-userspace/auparse/signaltab.h

## Purpose
Maps signal numbers to signal names for syscall argument and clone flag interpretation.

## Important APIs, types, and functions
The `_S` table covers signals `0..31`, including standard POSIX signals and Linux-specific names.

## Control flow
Generated `signal_i2s` is called by `interpret.c:print_signals` and `print_clone_flags`.

## State and persistence behavior
Static table only.

## Dependencies and integration points
Tracks asm-generic signal numbering. Integrated with kill/tkill/tgkill, `rt_sigaction`, `prctl`, and clone signal decoding.

## Risks and test signals
Risks are architecture-specific signal numbering and missing realtime signals. Tests should cover common signals, signal zero, clone low-byte signal output, and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/signaltab.h -->
