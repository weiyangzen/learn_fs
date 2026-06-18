<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/run_init/Makefile -->
# sources/security-integrity/selinux/policycoreutils/run_init/Makefile

## Purpose
Builds and installs the `run_init` and `open_init_pty` utilities used to execute init scripts under the correct SELinux context and PTY label.

## Important APIs, Types, And Functions
Variables configure install roots (`SBINDIR`, `MANDIR`, `ETCDIR`, `LOCALEDIR`), feature detection (`PAMH`, `AUDITH`), compiler flags for NLS/PAM/audit, and libselinux linkage through `LIBSELINUX_LDLIBS`. `TARGETS` is derived from local `.c` files. `open_init_pty` links with `-ldl -lutil`.

## Control Flow
`all` builds every C file as a binary. The PAM build path adds `-DUSE_PAM` and links PAM libraries; otherwise it enables shadow/crypt support. The audit header enables `-DUSE_AUDIT`. `install` creates sbin/man directories, installs both binaries and man pages, localized man pages, and `run_init.pamd` when PAM is available. `relabel` restores labels on installed binaries.

## State And Persistence
The Makefile creates binary artifacts and may install a PAM service file under `/etc/pam.d/run_init`.

## Dependencies And Integration Points
It is part of policycoreutils recursion and depends on libselinux, optional PAM, optional libaudit, `libutil` for PTY support, and localized man page directories.

## Risks And Edge Cases
Feature detection depends on host header locations, which can make cross builds inconsistent. PAM installs require `$(DESTDIR)$(ETCDIR)/pam.d` to exist or be creatable.

## Test Signals
Successful builds with and without PAM/audit, a working `open_init_pty` link, and restorecon success on installed paths are the primary signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/run_init/Makefile -->
