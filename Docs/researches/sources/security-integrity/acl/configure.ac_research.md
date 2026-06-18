<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/configure.ac -->
# sources/security-integrity/acl/configure.ac

Purpose: Autoconf entry point for the acl package, declaring package metadata, compiler/libtool/gettext setup, debug flags, large-file and endian checks, libattr/xattr dependency probes, generated include symlinks, and configured files. The file is 74 lines.

Important APIs and targets: Important declarations or variables include No exported code symbols; the file is declarative or script-oriented.. These names form build-system contracts rather than runtime C APIs.

Control flow: `autoreconf` expands macros, `configure` probes the host, substitutes `LT_REVISION`, creates `include/config.h`, arranges `include/acl` and `include/sys` symlinks, emits `Makefile`, `po/Makefile.in`, and `libacl.pc`.

State and persistence: State is persisted in generated build artifacts, installed files, distribution tarballs, symlinked include directories, or pkg-config metadata. The file itself does not maintain runtime process state.

Dependencies and integration points: Depends on GNU Autoconf/Automake/Libtool/Gettext conventions, the local module include layout, libattr/xattr probes, and package install variables. It integrates source files into the library, tool, documentation, test, or packaging surfaces.

Risks: Small target-list mistakes can silently omit files from builds, releases, installed docs, or tests. Versioning and dependency changes in libacl metadata affect ABI consumers and downstream pkg-config builds. Bootstrap/configure files are also sensitive to host portability and macro availability.

Test signals: Useful checks are `autoreconf -f -i`, `./configure`, `make`, `make check`, `make distcheck`, generated `libacl.pc` inspection, and verifying installed headers/manpages/tools match the module lists.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/configure.ac -->
