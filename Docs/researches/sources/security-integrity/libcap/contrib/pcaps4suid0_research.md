<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/pcaps4suid0 -->
# sources/security-integrity/libcap/contrib/pcaps4suid0

## Purpose
Legacy helper script for converting setuid-root binaries to file capabilities, with either inheritable/effective or permitted/effective semantics.

## Important APIs, Types, And Functions
Defines capability variables for `ping`, `traceroute`, `chsh`, `chfn`, `Xorg`, `chage`, `passwd`, `unix_chkpwd`, `mount`, and `umount`, `APPSARRAY`, `SET`, `p4s_test`, `p4s_app_convert`, `p4s_app_revert`, `p4s_convert`, `p4s_revert`, and `p4s_usage`.

## Control Flow
Checks root and required tools, resolves binaries with `which -a`, ignores symlinks, removes setuid and applies `setcap` on convert, or restores setuid and removes filecap on revert. CLI supports convert/revert/help.

## State And Persistence Behavior
Mutates system binary mode bits and file capability xattrs. These changes persist and alter privilege behavior for users.

## Dependencies And Integration Points
Requires root, `which`, `chmod`, `setcap`, file xattrs, and kernel file capability support.

## Risks And Edge Cases
Hard-coded numeric capability IDs are less readable and may age poorly. The array loop misses the last element because it stops at `COUNTER == UPPER`. The conversion can weaken or break system authentication/mount behavior.

## Test Signals
Signals are visible setuid-bit changes and `getcap`/`setcap -r` effects, though the script itself does not verify with `getcap`.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/pcaps4suid0 -->
