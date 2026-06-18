<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/setenforce.c -->
# sources/security-integrity/selinux/libselinux/utils/setenforce.c

## Purpose
CLI for changing SELinux enforcing/permissive mode.

## Important APIs, Types, And Functions
Accepts `Enforcing`, `Permissive`, `1`, or `0`; checks `is_selinux_enabled()` and calls `security_setenforce()`.

## Control Flow
Invalid args print usage. Disabled SELinux returns `1`; set failure returns `2`; success returns `0`.

## State And Persistence Behavior
Changes kernel enforcing mode through selinuxfs.

## Dependencies And Integration Points
Thin wrapper over `src/setenforce.c`.

## Risks And Test Signals
Test numeric/text case-insensitive inputs, disabled SELinux, permission denied, invalid values, and mode actually changing.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/setenforce.c -->
