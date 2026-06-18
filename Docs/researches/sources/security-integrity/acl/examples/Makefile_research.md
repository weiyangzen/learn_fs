<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/examples/Makefile -->
# sources/security-integrity/acl/examples/Makefile

Purpose: Example build/distribution metadata for sample ACL programs and the generated examples Makefile. The file is 9 lines.

Important APIs and targets: Important declarations or variables include `CFLAGS`, `LDFLAGS`, `PROGS`, `all`, `clean`. These names form build-system contracts rather than runtime C APIs.

Control flow: The module marks examples for distribution; the concrete examples Makefile invokes compiler and linker commands against installed or built libacl/libattr objects.

State and persistence: State is persisted in generated build artifacts, installed files, distribution tarballs, symlinked include directories, or pkg-config metadata. The file itself does not maintain runtime process state.

Dependencies and integration points: Depends on GNU Autoconf/Automake/Libtool/Gettext conventions, the local module include layout, libattr/xattr probes, and package install variables. It integrates source files into the library, tool, documentation, test, or packaging surfaces.

Risks: Small target-list mistakes can silently omit files from builds, releases, installed docs, or tests. Versioning and dependency changes in libacl metadata affect ABI consumers and downstream pkg-config builds. Bootstrap/configure files are also sensitive to host portability and macro availability.

Test signals: Useful checks are `autoreconf -f -i`, `./configure`, `make`, `make check`, `make distcheck`, generated `libacl.pc` inspection, and verifying installed headers/manpages/tools match the module lists.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/examples/Makefile -->
