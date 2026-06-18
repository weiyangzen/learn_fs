<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/include/acl_ea.h -->
# sources/security-integrity/acl/include/acl_ea.h

Purpose: Defines the Linux extended-attribute wire format for POSIX ACLs, including xattr names, version, little-endian header/entry layout, and size calculation helpers. The file is 52 lines.

Important APIs and types: Key declarations include `acl_ea_size`, `acl_ea_count`, `ACL_EA_ACCESS`, `ACL_EA_DEFAULT`, `ACL_EA_VERSION`.

Control flow: `acl_get_*` reads bytes from `system.posix_acl_access` or `system.posix_acl_default`, serializers translate between this layout and internal ACL entries, and setters write it back.

State and persistence: The header itself has no runtime storage, but it defines state shape for ACL handles, xattr records, traversal flags, formatting options, or tool callback arguments that other files allocate and persist through memory, xattrs, installed headers, or CLI behavior.

Dependencies and integration points: Integrates with `sys/types.h`, POSIX ACL conventions, libattr/xattr names, the private libobj allocator, libmisc utilities, command-line tools, and Autotools-generated `config.h`/visibility macros where applicable.

Risks: Endianness, packed layout, and xattr names are kernel/user-space interoperability contracts; any drift corrupts stored ACLs. Macro definitions and constants are especially sensitive because many source files compile behavior directly from them.

Test signals: Build all library/tools, run API manpage examples, validate text round trips, xattr get/set on little- and big-endian assumptions, recursive tool behavior, and downstream compilation against installed headers.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/include/acl_ea.h -->
