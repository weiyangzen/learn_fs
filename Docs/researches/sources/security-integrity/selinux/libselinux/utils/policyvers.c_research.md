<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/policyvers.c -->
# sources/security-integrity/selinux/libselinux/utils/policyvers.c

## Purpose
Prints the kernel policy version.

## Important APIs, Types, And Functions
Calls `security_policyvers()` and prints the integer.

## Control Flow
On API failure, reports strerror and exits `2`; otherwise exits success.

## State And Persistence Behavior
Read-only selinuxfs access.

## Dependencies And Integration Points
Thin wrapper over `src/policyvers.c`.

## Risks And Test Signals
Test missing selinuxfs, malformed policyvers, default fallback for missing file, and valid version output.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/policyvers.c -->
