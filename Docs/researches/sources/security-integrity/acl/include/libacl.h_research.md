<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/include/libacl.h -->
# sources/security-integrity/acl/include/libacl.h

Purpose: Public libacl extension header layered on `sys/acl.h`, adding text formatting flags, ACL validation error codes, comparison/check/equiv/extended-file helpers, and permission-copy APIs. The file is 80 lines.

Important APIs and types: Key declarations include `acl_cmp`, `acl_check`, `acl_from_mode`, `acl_equiv_mode`, `acl_extended_file`, `acl_extended_file_nofollow`, `acl_extended_fd`, `acl_entries`, `acl_get_perm`, `perm_copy_file`, `perm_copy_fd`, `__ACL_LIBACL_H`, `TEXT_SOME_EFFECTIVE`, `TEXT_ALL_EFFECTIVE`.

Control flow: Command-line tools and downstream applications use these helpers for richer ACL display, validation diagnostics, mode equivalence, extended ACL checks, and cp-style permission preservation.

State and persistence: The header itself has no runtime storage, but it defines state shape for ACL handles, xattr records, traversal flags, formatting options, or tool callback arguments that other files allocate and persist through memory, xattrs, installed headers, or CLI behavior.

Dependencies and integration points: Integrates with `sys/types.h`, POSIX ACL conventions, libattr/xattr names, the private libobj allocator, libmisc utilities, command-line tools, and Autotools-generated `config.h`/visibility macros where applicable.

Risks: The extension API is public; exported names and error-code meanings are consumed by tools such as `getfacl`, `setfacl`, and external programs. Macro definitions and constants are especially sensitive because many source files compile behavior directly from them.

Test signals: Build all library/tools, run API manpage examples, validate text round trips, xattr get/set on little- and big-endian assumptions, recursive tool behavior, and downstream compilation against installed headers.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/include/libacl.h -->
