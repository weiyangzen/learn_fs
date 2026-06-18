<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/perm_copy.h -->
# sources/security-integrity/acl/libacl/perm_copy.h

Purpose: Compatibility feature-detection shim forced into libacl permission-copy compilation to declare which ACL/libattr APIs are available in this package build. The file is 40 lines.

Important APIs and types: Key declarations include `HAVE_ACL_LIBACL_H`, `HAVE_CONFIG_H`, `HAVE_SYS_ACL_H`, `HAVE_LIBACL_LIBACL_H`, `HAVE_ACL_DELETE_DEF_FILE`, `HAVE_ACL_ENTRIES`, `HAVE_ACL_FREE`, `HAVE_ACL_FROM_MODE`, `HAVE_ACL_FROM_TEXT`, `HAVE_ACL_GET_ENTRY`.

Control flow: `perm_copy_file.c` and `perm_copy_fd.c` use these macros to select native ACL preservation or chmod-only fallbacks.

State and persistence: The header itself has no runtime storage, but it defines state shape for ACL handles, xattr records, traversal flags, formatting options, or tool callback arguments that other files allocate and persist through memory, xattrs, installed headers, or CLI behavior.

Dependencies and integration points: Integrates with `sys/types.h`, POSIX ACL conventions, libattr/xattr names, the private libobj allocator, libmisc utilities, command-line tools, and Autotools-generated `config.h`/visibility macros where applicable.

Risks: Wrong feature macros change error handling and may drop extended ACLs silently. Macro definitions and constants are especially sensitive because many source files compile behavior directly from them.

Test signals: Build all library/tools, run API manpage examples, validate text round trips, xattr get/set on little- and big-endian assumptions, recursive tool behavior, and downstream compilation against installed headers.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/perm_copy.h -->
