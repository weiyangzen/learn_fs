<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selinuxenabled.c -->
# sources/security-integrity/selinux/libselinux/utils/selinuxenabled.c

## Purpose
Provides a shell-friendly test for whether SELinux is enabled.

## Important APIs, Types, And Functions
`main()` returns `!is_selinux_enabled()`.

## Control Flow
Enabled returns exit `0`; disabled returns nonzero. Negative error values become nonzero as well.

## State And Persistence Behavior
Read-only.

## Dependencies And Integration Points
Used by shell scripts and build/runtime checks.

## Risks And Test Signals
Test enabled, disabled, and error states; note that errors are not distinguished from enabled/disabled in output because there is no output.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/utils/selinuxenabled.c -->
