<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selinux_check_access.c -->
# sources/security-integrity/selinux/libselinux/utils/selinux_check_access.c

## Purpose
CLI for checking whether a source context has a permission on a target context/class.

## Important APIs, Types, And Functions
Optional `-a auditdata` installs an audit callback that copies the string into the audit message. Then `selinux_check_access()` is called with `scon tcon class perm`.

## Control Flow
Requires four operands after options; returns the libselinux check result and prints perror on failure.

## State And Persistence Behavior
Read-only policy query, but it mutates the process-global SELinux audit callback when `-a` is supplied.

## Dependencies And Integration Points
Exercises high-level access-check API and callback plumbing.

## Risks And Test Signals
Test allowed and denied checks, invalid classes/perms, audit callback content, missing args, and callback side effects in long-lived processes.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selinux_check_access.c -->
