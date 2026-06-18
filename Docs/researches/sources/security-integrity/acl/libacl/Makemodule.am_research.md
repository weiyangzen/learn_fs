<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/Makemodule.am -->
# sources/security-integrity/acl/libacl/Makemodule.am

Purpose: Source file participating in the ACL package. The file is 83 lines.

Important APIs and functions: Key symbols include `lib_LTLIBRARIES`, `LT_CURRENT`, `LT_AGE`, `LTVERSION`, `CFILES`, `HFILES`, `POSIX_CFILES`, `LIBACL_CFILES`, `INTERNAL_CFILES`, `libacl_la_DEPENDENCIES`, `libacl_la_SOURCES`, `libacl_la_LIBADD`, `libacl_la_CFLAGS`, `libacl_la_LDFLAGS`.

Control flow: The file contributes declarative or helper behavior used by the surrounding ACL build, library, tool, or test subsystem.

State and persistence: State is local to the consuming subsystem and is persisted only through generated build/test artifacts or filesystem ACL operations performed by callers.

Dependencies and integration points: Integrates with the acl source tree's Autotools build, libacl/libmisc internals, public ACL headers, tools, or tests depending on its directory.

Risks: Drift from adjacent module contracts can break builds, tests, or command behavior.

Test signals: Build the package, run `make check`, and exercise the relevant public tool or API path.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/Makemodule.am -->
