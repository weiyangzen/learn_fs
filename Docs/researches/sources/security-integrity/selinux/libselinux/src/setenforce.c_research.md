<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/setenforce.c -->
# sources/security-integrity/selinux/libselinux/src/setenforce.c

## Purpose
Sets the kernel SELinux enforcing mode.

## Important APIs, Types, And Functions
`security_setenforce()` writes `0` or `1` as text to `<selinux_mnt>/enforce`.

## Control Flow
The function validates `selinux_mnt`, opens the control file read-write, writes the formatted integer, closes, and returns success on nonnegative write.

## State And Persistence Behavior
Persists immediate kernel enforcing-state change through selinuxfs.

## Dependencies And Integration Points
Used by init policy loading and the `setenforce` utility.

## Risks And Test Signals
Test missing mount, permission denied, invalid values accepted/rejected by kernel, write errors, and caller behavior when SELinux is disabled.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/setenforce.c -->
