<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/policyvers.c -->
# sources/security-integrity/selinux/libselinux/src/policyvers.c

## Purpose
Reads the running kernel SELinux policy version.

## Important APIs, Types, And Functions
`security_policyvers()` opens `<selinux_mnt>/policyvers`, parses an unsigned version, and returns `DEFAULT_POLICY_VERSION` when the control file is absent.

## Control Flow
The function fails with `ENOENT` if `selinux_mnt` is unset, otherwise reads a small fixed buffer and parses it with `sscanf()`.

## State And Persistence Behavior
It is read-only and depends entirely on selinuxfs state.

## Dependencies And Integration Points
Used by policy loading and the `policyvers` utility; depends on `policy.h` and `selinux_internal.h`.

## Risks And Test Signals
Test missing mount, missing `policyvers`, unreadable file, malformed content, and valid versions. The fallback default is important for older kernels.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/policyvers.c -->
