<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/normalize_record_map.h -->
# sources/security-integrity/audit-userspace/auparse/normalize_record_map.h

## Purpose
Maps audit record types to normalized action phrases for non-syscall or record-driven events.

## Important APIs, types, and functions
The `_S` table maps many `AUDIT_*` constants to phrases such as `authenticated`, `started-session`, `changed-audit-configuration`, `typed`, `accessed-mac-policy-controlled-object`, `loaded-selinux-policy`, `crashed-program`, and virtualization/crypto actions.

## Control flow
Generated `normalize_record_map_i2s` is called throughout `normalize_simple` and for special compound cases when action derives from record type rather than syscall.

## State and persistence behavior
Static mapping only.

## Dependencies and integration points
Depends on `libaudit.h` record constants and integrates with normalization action selection.

## Risks and test signals
Risks are incomplete mappings returning null action, typo/stability issues in user-facing phrases, and new audit record types falling to unknown behavior. Tests should cover user, daemon, MAC, anomaly, crypto, virt, and config record actions.
<!-- END_FILE_RESEARCH: sources/security-integrity/audit-userspace/auparse/normalize_record_map.h -->
