<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/acl/libacl/libobj.h -->
# sources/security-integrity/acl/libacl/libobj.h

Purpose: Private object-system header that prepends magic/flag metadata to allocated libacl objects and provides checked allocation, conversion, and free macros. The file is 96 lines.

Important APIs and types: Key declarations include `__LIBOBJ_H`, `int2ext`, `new_var_obj_p`, `realloc_var_obj_p`, `new_obj_p`, `new_obj_p_here`, `check_obj_p`, `free_obj_p`, `pmagic`, `pflags`.

Control flow: Allocation creates tagged objects, public handles point into embedded external structs, and API entry points validate handles before mutation.

State and persistence: The header itself has no runtime storage, but it defines state shape for ACL handles, xattr records, traversal flags, formatting options, or tool callback arguments that other files allocate and persist through memory, xattrs, installed headers, or CLI behavior.

Dependencies and integration points: Integrates with `sys/types.h`, POSIX ACL conventions, libattr/xattr names, the private libobj allocator, libmisc utilities, command-line tools, and Autotools-generated `config.h`/visibility macros where applicable.

Risks: The conversion macros are intentionally low-level pointer manipulation; misuse can cause invalid frees or false handle validation. Macro definitions and constants are especially sensitive because many source files compile behavior directly from them.

Test signals: Build all library/tools, run API manpage examples, validate text round trips, xattr get/set on little- and big-endian assumptions, recursive tool behavior, and downstream compilation against installed headers.
<!-- END_FILE_RESEARCH: sources/security-integrity/acl/libacl/libobj.h -->
