<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/pcaps4convenience -->
# sources/security-integrity/libcap/contrib/pcaps4convenience

## Purpose
Legacy helper script for assigning inheritable/effective file capabilities to convenience binaries such as `eject`, `killall`, `modprobe`, `ntpdate`, `qemu`, and `route`.

## Important APIs, Types, And Functions
Defines capability variables, `APPSARRAY`, `SET=ie`, `p4c_test`, `p4c_app_convert`, `p4c_app_revert`, `p4c_convert`, `p4c_revert`, and `p4c_usage`.

## Control Flow
Validates root and `setcap`, resolves each application with `which -a`, skips symlinks, applies `setcap <caps>=ie` on convert, or removes capabilities on revert. CLI supports `con|convert`, `rev|revert`, and `help`.

## State And Persistence Behavior
Mutates file capability xattrs on system binaries. Does not change setuid bits.

## Dependencies And Integration Points
Requires root, `which`, `setcap`, and filesystem/kernel file capability support. Intended to pair with PAM-managed inheritable capabilities.

## Risks And Edge Cases
Hard-coded capability sets may be obsolete or unsafe. The loop condition stops before the final array element. Shell tests use unquoted paths and fragile `==` expressions.

## Test Signals
Signals are `setcap` success/removal for each found non-symlink binary and usage output for invalid commands.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/pcaps4convenience -->
