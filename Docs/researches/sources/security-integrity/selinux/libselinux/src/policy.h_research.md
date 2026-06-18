<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/policy.h -->
# sources/security-integrity/selinux/libselinux/src/policy.h

## Purpose
Defines private libselinux constants for selinuxfs, policy file defaults, and SELinux xattr names.

## Important APIs, Types, And Functions
Exports `XATTR_NAME_SELINUX`, `INITCONTEXTLEN`, `SELINUXFS`, `SELINUX_MAGIC`, `SELINUXMNT`, `OLDSELINUXMNT`, `FILECONTEXTS`, `DEFAULT_POLICY_VERSION`, and the external `selinux_mnt`.

## Control Flow
No executable control flow exists.

## State And Persistence Behavior
`selinux_mnt` is mutable process-global state managed elsewhere and used by many selinuxfs accessors.

## Dependencies And Integration Points
Included by policy loaders, xattr setters, selinuxfs readers/writers, stringrep, and validation code.

## Risks And Test Signals
Risks are stale defaults relative to kernel/userland layout and inconsistent use of `selinux_mnt`. Compile coverage plus tests against both `/sys/fs/selinux` and legacy `/selinux` paths are relevant.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/policy.h -->
