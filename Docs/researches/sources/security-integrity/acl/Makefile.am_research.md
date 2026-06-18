<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/Makefile.am -->
# sources/security-integrity/acl/Makefile.am

Purpose: Top-level Automake include file that defines the distribution root, `SUBDIRS = po`, common compiler flags, placeholder build variables, and includes module fragments for docs, headers, libraries, tools, tests, examples, and man pages. The file is 36 lines.

Important APIs and targets: Important declarations or variables include `ACLOCAL_AMFLAGS`, `EXTRA_DIST`, `SUBDIRS`, `AM_CPPFLAGS`, `pkgconfdir`, `sysincludedir`, `pkgconf_DATA`, `pkginclude_HEADERS`, `sysinclude_HEADERS`, `bin_PROGRAMS`, `lib_LTLIBRARIES`, `noinst_HEADERS`, `noinst_LTLIBRARIES`, `dist_doc_DATA`. These names form build-system contracts rather than runtime C APIs.

Control flow: Automake reads this file first, initializes empty aggregate variables such as `bin_PROGRAMS`, `noinst_HEADERS`, `dist_doc_DATA`, and `dist_man_MANS`, then each included `Makemodule.am` appends targets and source lists.

State and persistence: State is persisted in generated build artifacts, installed files, distribution tarballs, symlinked include directories, or pkg-config metadata. The file itself does not maintain runtime process state.

Dependencies and integration points: Depends on GNU Autoconf/Automake/Libtool/Gettext conventions, the local module include layout, libattr/xattr probes, and package install variables. It integrates source files into the library, tool, documentation, test, or packaging surfaces.

Risks: Small target-list mistakes can silently omit files from builds, releases, installed docs, or tests. Versioning and dependency changes in libacl metadata affect ABI consumers and downstream pkg-config builds. Bootstrap/configure files are also sensitive to host portability and macro availability.

Test signals: Useful checks are `autoreconf -f -i`, `./configure`, `make`, `make check`, `make distcheck`, generated `libacl.pc` inspection, and verifying installed headers/manpages/tools match the module lists.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/Makefile.am -->
