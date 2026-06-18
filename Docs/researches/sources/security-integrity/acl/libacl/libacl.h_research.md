<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/libacl.h -->
# sources/security-integrity/acl/libacl/libacl.h

Purpose: Private libacl implementation header mapping public opaque handles to tagged internal objects, defining ACL entry/qualifier/permset containers, object macros, canonical iteration, and hidden helper prototypes. The file is 150 lines.

Important APIs and types: Key declarations include `ACL_PERM_NONE`, `sperm`, `oprefix`, `permset_obj_equal`, `qid`, `qualifier_obj_id`, `econtainer`, `eprev`, `enext`, `eentry`.

Control flow: All libacl C files convert external handles through `ext2int`, mutate linked-list ACL objects, and return handles through `int2ext`.

State and persistence: The header itself has no runtime storage, but it defines state shape for ACL handles, xattr records, traversal flags, formatting options, or tool callback arguments that other files allocate and persist through memory, xattrs, installed headers, or CLI behavior.

Dependencies and integration points: Integrates with `sys/types.h`, POSIX ACL conventions, libattr/xattr names, the private libobj allocator, libmisc utilities, command-line tools, and Autotools-generated `config.h`/visibility macros where applicable.

Risks: Pointer-prefix and magic-check macros are central memory-safety guards; layout changes affect every API implementation. Macro definitions and constants are especially sensitive because many source files compile behavior directly from them.

Test signals: Build all library/tools, run API manpage examples, validate text round trips, xattr get/set on little- and big-endian assumptions, recursive tool behavior, and downstream compilation against installed headers.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/libacl.h -->
