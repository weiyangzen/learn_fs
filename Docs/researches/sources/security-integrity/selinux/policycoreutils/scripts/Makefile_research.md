<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/scripts/Makefile -->
# sources/security-integrity/selinux/policycoreutils/scripts/Makefile

## Purpose
Installs the shell-script utilities in the policycoreutils scripts directory, currently centered on `fixfiles`.

## Important APIs, Types, And Functions
Defines `PREFIX`, `SBINDIR`, `MANDIR`, `LINGUAS`, and targets `all`, `install`, `clean`, and `relabel`. `all` depends on the executable script `fixfiles`.

## Control Flow
`install` creates the sbin and man8 destinations, installs `fixfiles` as mode 755, installs `fixfiles.8`, and copies localized man pages from language subdirectories when `LINGUAS` entries exist.

## State And Persistence
Only installed script and man page files are persisted. `clean` and `relabel` are no-op placeholders.

## Dependencies And Integration Points
This Makefile is invoked by the policycoreutils parent build. The installed script expects system tools such as `restorecon`, `setfiles`, `find`, `rpm`, `mount`, `unshare`, and SELinux utilities.

## Risks And Edge Cases
The target does not validate script syntax or dependency availability. `LINGUAS` handling assumes each language directory contains matching man8 pages.

## Test Signals
Useful signals are successful install into a staging `DESTDIR`, correct executable mode on `fixfiles`, correct man page placement, and shell syntax checks run separately against the script.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/scripts/Makefile -->
