<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/getenforce.c -->
# sources/security-integrity/selinux/libselinux/utils/getenforce.c

## Purpose
Prints SELinux mode as `Enforcing`, `Permissive`, or `Disabled`.

## Important APIs, Types, And Functions
`main()` calls `is_selinux_enabled()` and, when enabled, `security_getenforce()`.

## Control Flow
Failure to query enabled/enforcing state returns `2`; disabled and successful states return `0`.

## State And Persistence Behavior
Read-only selinuxfs access.

## Dependencies And Integration Points
Thin CLI over core mode APIs.

## Risks And Test Signals
Test enabled permissive/enforcing, disabled, and error paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/getenforce.c -->
