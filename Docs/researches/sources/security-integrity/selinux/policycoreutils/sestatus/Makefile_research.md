<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/sestatus/Makefile -->
# sources/security-integrity/selinux/policycoreutils/sestatus/Makefile

## Purpose
Builds and installs `sestatus`, its configuration file, man pages, and a compatibility symlink in sbin.

## Important APIs, Types, And Functions
Defines `BINDIR`, `SBINDIR`, `MANDIR`, `ETCDIR`, libselinux include/library flags, and `_FILE_OFFSET_BITS=64`. Targets include `sestatus`, `install`, `clean`, and `relabel`.

## Control Flow
`all` builds `sestatus`. `install` creates man and binary directories, creates a relative sbin symlink to the bindir binary for tools that hard-code `/usr/sbin/sestatus`, installs the binary, installs man8/man5 files, localized man pages, and installs `sestatus.conf` under `$(ETCDIR)`.

## State And Persistence
Persists the executable, symlink, man pages, and `/etc/sestatus.conf`.

## Dependencies And Integration Points
Depends on libselinux and system packaging conventions where `BINDIR` and `SBINDIR` may differ or be identical.

## Risks And Edge Cases
The relative symlink creation must behave correctly under `DESTDIR`; unusual install tools or non-GNU `ln` may differ. Existing symlinks are deliberately overwritten before binary install.

## Test Signals
Staged install should show a working binary in bindir, correct sbin symlink, installed config, and successful execution against active or disabled SELinux.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/sestatus/Makefile -->
