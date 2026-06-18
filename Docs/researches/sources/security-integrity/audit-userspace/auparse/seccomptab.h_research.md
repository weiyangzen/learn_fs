<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/seccomptab.h -->
# sources/security-integrity/audit-userspace/auparse/seccomptab.h

## Purpose
Maps seccomp return action bits to normalized strings.

## Important APIs, types, and functions
The `_S` table maps seccomp action masks to `kill-process`, `kill-thread`, `trap`, `errno`, `user-notify`, `trace`, `log`, and `allow`.

## Control flow
Generated `seccomp_i2s` is called by `interpret.c:print_seccomp_code` after masking with `SECCOMP_RET_ACTION`.

## State and persistence behavior
Static table only.

## Dependencies and integration points
Tracks `include/uapi/linux/seccomp.h` and feeds `AUPARSE_TYPE_SECCOMP`; normalization treats seccomp as DAC-decision style event.

## Risks and test signals
Risks are missing future actions and incorrect masking of data bits. Tests should include action values with lower data bits set and unknown fallback.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/seccomptab.h -->
