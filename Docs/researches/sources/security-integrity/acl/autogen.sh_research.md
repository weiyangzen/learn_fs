<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/autogen.sh -->
# sources/security-integrity/acl/autogen.sh

Purpose: Bootstrap helper that reruns the GNU build-system generator stack for a checkout. The file is 6 lines.

Important APIs and targets: Important declarations or variables include No exported code symbols; the file is declarative or script-oriented.. These names form build-system contracts rather than runtime C APIs.

Control flow: The script exits on errors and `exec`s `autoreconf -f -i`, replacing itself with autoreconf so generated aux files, macros, and Makefile templates are refreshed.

State and persistence: State is persisted in generated build artifacts, installed files, distribution tarballs, symlinked include directories, or pkg-config metadata. The file itself does not maintain runtime process state.

Dependencies and integration points: Depends on GNU Autoconf/Automake/Libtool/Gettext conventions, the local module include layout, libattr/xattr probes, and package install variables. It integrates source files into the library, tool, documentation, test, or packaging surfaces.

Risks: Small target-list mistakes can silently omit files from builds, releases, installed docs, or tests. Versioning and dependency changes in libacl metadata affect ABI consumers and downstream pkg-config builds. Bootstrap/configure files are also sensitive to host portability and macro availability.

Test signals: Useful checks are `autoreconf -f -i`, `./configure`, `make`, `make check`, `make distcheck`, generated `libacl.pc` inspection, and verifying installed headers/manpages/tools match the module lists.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/autogen.sh -->
