<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsrahead/Makefile.am -->
# sources/user-network-fs/nfs-utils/tools/nfsrahead/Makefile.am

## Purpose

This Automake file builds the `nfsrahead` udev helper, installs its manual page, and generates/installs the udev rule.

## Important APIs, Types, and Functions

It declares `libexec_PROGRAMS = nfsrahead`, builds `main.c`, links with `$(LIBMOUNT_LIBS)` and `../../support/nfs/libnfsconf.la`, installs `nfsrahead.man`, defines `udev_rulesdir = /usr/lib/udev/rules.d/`, and generates `99-nfs.rules` from the `.in` file via `$(SED)`.

## Control Flow

Build compiles the helper and substitutes `_libexecdir_` in the template. Install places the helper in `libexecdir`, the rule in the udev rules directory, and the man page. `clean-local` removes the generated rule.

## State and Persistence Behavior

No runtime state exists in the build file. It controls persistent installed paths for the helper, documentation, and udev rule.

## Dependencies and Integration Points

It integrates libmount-based mount discovery, nfsconf configuration parsing, and udev. It depends on generated `builddefs` and configured `LIBMOUNT_LIBS`.

## Risks and Edge Cases

The hard-coded udev rules directory may not match all distributions. Linker flags use `nfsrahead_LDFLAGS = $(LIBMOUNT_LIBS)` rather than `LDADD` for libmount, which packaging/build environments should verify.

## Test Signals

Build and install tests should verify helper linkage, generated rule substitution, clean removal of generated rules, and correct install directories under `DESTDIR`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsrahead/Makefile.am -->
