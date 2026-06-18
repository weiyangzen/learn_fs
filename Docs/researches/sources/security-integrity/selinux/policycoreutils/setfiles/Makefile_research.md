<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/setfiles/Makefile -->
# sources/security-integrity/selinux/policycoreutils/setfiles/Makefile

## Purpose
Builds and installs `setfiles`, its `restorecon` symlink, and `restorecon_xattr`.

## Important APIs, Types, And Functions
Defines `/sbin` as default `SBINDIR`, audit header detection, libselinux/libsepol/pthread linkage, and optional libaudit flags. Targets are `setfiles`, `restorecon`, `restorecon_xattr`, `install`, `clean`, and `relabel`.

## Control Flow
`all` builds `setfiles restorecon restorecon_xattr`. `setfiles` links `setfiles.o restore.o`; `restorecon` is a symlink to `setfiles`; `restorecon_xattr` links `restorecon_xattr.o restore.o`. Install copies binaries, creates the symlink, installs man pages and localized man pages. `relabel` runs the installed `restorecon` on installed binaries.

## State And Persistence
Produces binaries, symlinks, and installed man pages; `relabel` can mutate labels on installed utility files.

## Dependencies And Integration Points
Depends on libselinux restorecon APIs, libsepol, pthreads for parallel restorecon, and optional audit.

## Risks And Edge Cases
The behavior of `setfiles` versus `restorecon` is selected by argv0, so symlink correctness is functional. Default `/sbin` install path may differ from distribution policy.

## Test Signals
Check that both argv0 modes exist, `restorecon` symlink points to `setfiles`, optional audit builds work, and staged relabel targets only installed utility files.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/setfiles/Makefile -->
