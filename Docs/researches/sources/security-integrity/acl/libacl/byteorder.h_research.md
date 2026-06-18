<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/byteorder.h -->
# sources/security-integrity/acl/libacl/byteorder.h

Purpose: Endian-conversion compatibility layer for ACL xattr serialization, selecting host-to/from little-endian conversion helpers based on configure results. The file is 33 lines.

Important APIs and types: Key declarations include No exported code symbols; the file is declarative or script-oriented..

Control flow: xattr readers and writers call `cpu_to_le16/32` and `le16/32_to_cpu` through this header when translating kernel ACL bytes.

State and persistence: The header itself has no runtime storage, but it defines state shape for ACL handles, xattr records, traversal flags, formatting options, or tool callback arguments that other files allocate and persist through memory, xattrs, installed headers, or CLI behavior.

Dependencies and integration points: Integrates with `sys/types.h`, POSIX ACL conventions, libattr/xattr names, the private libobj allocator, libmisc utilities, command-line tools, and Autotools-generated `config.h`/visibility macros where applicable.

Risks: Incorrect endian branches make cross-architecture ACL xattrs unreadable or misinterpreted. Macro definitions and constants are especially sensitive because many source files compile behavior directly from them.

Test signals: Build all library/tools, run API manpage examples, validate text round trips, xattr get/set on little- and big-endian assumptions, recursive tool behavior, and downstream compilation against installed headers.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/byteorder.h -->
