<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/include/walk_tree.h -->
# sources/security-integrity/acl/include/walk_tree.h

Purpose: Internal directory traversal contract defining recursive, logical/physical symlink, top-level dereference, one-filesystem, failure, and callback flags. The file is 42 lines.

Important APIs and types: Key declarations include `walk_tree`, `__WALK_TREE_H`, `WALK_TREE_RECURSIVE`, `WALK_TREE_PHYSICAL`, `WALK_TREE_LOGICAL`, `WALK_TREE_DEREFERENCE`, `WALK_TREE_DEREFERENCE_TOPLEVEL`, `WALK_TREE_ONE_FILESYSTEM`, `WALK_TREE_TOPLEVEL`, `WALK_TREE_SYMLINK`, `WALK_TREE_FAILED`.

Control flow: Tools pass a path, flag set, optional fd budget, and callback; `walk_tree.c` reports each node with stat data and walk flags.

State and persistence: The header itself has no runtime storage, but it defines state shape for ACL handles, xattr records, traversal flags, formatting options, or tool callback arguments that other files allocate and persist through memory, xattrs, installed headers, or CLI behavior.

Dependencies and integration points: Integrates with `sys/types.h`, POSIX ACL conventions, libattr/xattr names, the private libobj allocator, libmisc utilities, command-line tools, and Autotools-generated `config.h`/visibility macros where applicable.

Risks: Flag semantics are user-visible through `getfacl -R/-L/-P` and `setfacl`; regressions can follow or skip symlinks incorrectly. Macro definitions and constants are especially sensitive because many source files compile behavior directly from them.

Test signals: Build all library/tools, run API manpage examples, validate text round trips, xattr get/set on little- and big-endian assumptions, recursive tool behavior, and downstream compilation against installed headers.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/include/walk_tree.h -->
