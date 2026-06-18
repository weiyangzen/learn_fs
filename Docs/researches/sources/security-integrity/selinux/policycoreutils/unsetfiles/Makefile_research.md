<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/unsetfiles/Makefile -->
# sources/security-integrity/selinux/policycoreutils/unsetfiles/Makefile

## Purpose
Builds and installs `unsetfiles`, a utility for removing SELinux xattrs on SELinux-disabled systems.

## Important APIs, Types, And Functions
Defines `PREFIX`, `SBINDIR`, `MANDIR`, libselinux include/library flags, and `-D_GNU_SOURCE`. Targets are `all`, `unsetfiles`, `install`, `clean`, and `relabel`.

## Control Flow
`all` builds `unsetfiles` from `unsetfiles.o`. `install` creates sbin and man1 directories, installs the binary and `unsetfiles.1`. `relabel` runs restorecon on the installed binary.

## State And Persistence
Build state is object/binary files; install persists the utility and man page.

## Dependencies And Integration Points
Depends on libselinux and system xattr support used by the C source.

## Risks And Edge Cases
The `relabel` target invokes `/sbin/restorecon`, which may be inappropriate when building for systems where SELinux is disabled, although it targets only the installed utility.

## Test Signals
Compile/link success, staged install, and runtime dry-run tests against xattr-capable filesystems.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/unsetfiles/Makefile -->
