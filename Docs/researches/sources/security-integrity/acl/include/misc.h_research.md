<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/include/misc.h -->
# sources/security-integrity/acl/include/misc.h

Purpose: Internal helper header for allocation growth, line reading, quoting/unquoting, and user/group id-name lookup used by libacl and tools. The file is 51 lines.

Important APIs and types: Key declarations include `__acl_high_water_alloc`, `__acl_get_uid`, `__acl_get_gid`, `__MISC_H`.

Control flow: Tools call quote and lookup helpers while parsers/text emitters call unquote and uid/gid resolution; buffers grow through high-water allocation.

State and persistence: The header itself has no runtime storage, but it defines state shape for ACL handles, xattr records, traversal flags, formatting options, or tool callback arguments that other files allocate and persist through memory, xattrs, installed headers, or CLI behavior.

Dependencies and integration points: Integrates with `sys/types.h`, POSIX ACL conventions, libattr/xattr names, the private libobj allocator, libmisc utilities, command-line tools, and Autotools-generated `config.h`/visibility macros where applicable.

Risks: Lookup and quoting behavior directly affects text ACL parsing, display stability, and shell/test expectations. Macro definitions and constants are especially sensitive because many source files compile behavior directly from them.

Test signals: Build all library/tools, run API manpage examples, validate text round trips, xattr get/set on little- and big-endian assumptions, recursive tool behavior, and downstream compilation against installed headers.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/include/misc.h -->
