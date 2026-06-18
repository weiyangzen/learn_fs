<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/tools/do_set.h -->
# sources/security-integrity/acl/tools/do_set.h

Purpose: Tool-private interface for `setfacl` application logic, declaring command execution state shared between parser/main code and `do_set.c`. The file is 40 lines.

Important APIs and types: Key declarations include `do_set`, `__DO_SET_H`.

Control flow: `setfacl.c` constructs a sequence of ACL commands, fills `do_set_args`, and passes `do_set` as the tree-walk callback.

State and persistence: The header itself has no runtime storage, but it defines state shape for ACL handles, xattr records, traversal flags, formatting options, or tool callback arguments that other files allocate and persist through memory, xattrs, installed headers, or CLI behavior.

Dependencies and integration points: Integrates with `sys/types.h`, POSIX ACL conventions, libattr/xattr names, the private libobj allocator, libmisc utilities, command-line tools, and Autotools-generated `config.h`/visibility macros where applicable.

Risks: Field semantics must remain aligned with parser command flags or setfacl may modify the wrong ACL type. Macro definitions and constants are especially sensitive because many source files compile behavior directly from them.

Test signals: Build all library/tools, run API manpage examples, validate text round trips, xattr get/set on little- and big-endian assumptions, recursive tool behavior, and downstream compilation against installed headers.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/tools/do_set.h -->
