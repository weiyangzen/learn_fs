<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/__acl_to_xattr.h -->
# sources/security-integrity/acl/libacl/__acl_to_xattr.h

Purpose: Private helper prototype header for one hidden libacl routine used across xattr or extended-ACL implementation files. The file is 1 lines.

Important APIs and types: Key declarations include No exported code symbols; the file is declarative or script-oriented..

Control flow: Implementation files include it to share hidden helper signatures without exposing them in public headers.

State and persistence: The header itself has no runtime storage, but it defines state shape for ACL handles, xattr records, traversal flags, formatting options, or tool callback arguments that other files allocate and persist through memory, xattrs, installed headers, or CLI behavior.

Dependencies and integration points: Integrates with `sys/types.h`, POSIX ACL conventions, libattr/xattr names, the private libobj allocator, libmisc utilities, command-line tools, and Autotools-generated `config.h`/visibility macros where applicable.

Risks: Prototype drift causes build warnings or ABI-internal mismatches. Macro definitions and constants are especially sensitive because many source files compile behavior directly from them.

Test signals: Build all library/tools, run API manpage examples, validate text round trips, xattr get/set on little- and big-endian assumptions, recursive tool behavior, and downstream compilation against installed headers.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/__acl_to_xattr.h -->
