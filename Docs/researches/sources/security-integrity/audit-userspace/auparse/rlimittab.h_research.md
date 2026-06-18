<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/rlimittab.h -->
# sources/security-integrity/audit-userspace/auparse/rlimittab.h

## Purpose
Maps resource limit ids to names for `setrlimit`/`getrlimit`-family interpretation.

## Important APIs, types, and functions
The `_S` table maps ids `0..15` to CPU, file size, data, stack, core, RSS, process count, file descriptor, memory lock, address space, locks, pending signals, message queue, nice, real-time priority, and real-time time limits.

## Control flow
Generated `rlimit_i2s` is called by `interpret.c:print_rlimit` for matching syscall arguments.

## State and persistence behavior
Static table only.

## Dependencies and integration points
Tracks asm-generic resource headers. Integrated via `print_a0` for `*etrlimit` syscall names.

## Risks and test signals
Risks are missing `RLIMIT_RTTIME`-adjacent additions and fixed `i < 17` bound mismatch. Tests should verify each known id and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/rlimittab.h -->
