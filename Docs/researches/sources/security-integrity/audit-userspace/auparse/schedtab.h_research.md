<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/schedtab.h -->
# sources/security-integrity/audit-userspace/auparse/schedtab.h

## Purpose
Maps Linux scheduler policy ids to names.

## Important APIs, types, and functions
The `_S` table covers `SCHED_OTHER`, `FIFO`, `RR`, `BATCH`, `IDLE`, and `DEADLINE`.

## Control flow
Generated `sched_i2s` is used by `interpret.c:print_sched`, which masks policy bits and appends `SCHED_RESET_ON_FORK` when set.

## State and persistence behavior
Static lookup data only.

## Dependencies and integration points
Tracks Linux sched headers and supports normalization of scheduler-related syscalls.

## Risks and test signals
Risks are missing policies and flag masking mistakes. Tests should cover policy names, reset-on-fork combination, and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/schedtab.h -->
