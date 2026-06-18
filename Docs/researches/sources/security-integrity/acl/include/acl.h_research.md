<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/include/acl.h -->
# sources/security-integrity/acl/include/acl.h

Purpose: Public POSIX.1e-style `sys/acl.h` compatibility API defining opaque ACL handle types, ACL tag/permission/type constants, and the core entry, permission, text, external-copy, file, and fd manipulation functions. The file is 127 lines.

Important APIs and types: Key declarations include `acl_init`, `acl_dup`, `acl_free`, `acl_valid`, `acl_copy_entry`, `acl_create_entry`, `acl_delete_entry`, `acl_get_entry`, `acl_add_perm`, `acl_calc_mask`, `acl_clear_perms`, `acl_delete_perm`, `acl_get_permset`, `acl_set_permset`.

Control flow: Callers allocate an `acl_t`, create or iterate entries, manipulate tag/qualifier/permission fields, validate or serialize it, then apply it to paths or file descriptors.

State and persistence: The header itself has no runtime storage, but it defines state shape for ACL handles, xattr records, traversal flags, formatting options, or tool callback arguments that other files allocate and persist through memory, xattrs, installed headers, or CLI behavior.

Dependencies and integration points: Integrates with `sys/types.h`, POSIX ACL conventions, libattr/xattr names, the private libobj allocator, libmisc utilities, command-line tools, and Autotools-generated `config.h`/visibility macros where applicable.

Risks: This header is a public ABI: numeric constants, opaque pointer typedefs, and exported prototypes must remain compatible with existing applications. Macro definitions and constants are especially sensitive because many source files compile behavior directly from them.

Test signals: Build all library/tools, run API manpage examples, validate text round trips, xattr get/set on little- and big-endian assumptions, recursive tool behavior, and downstream compilation against installed headers.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/include/acl.h -->
