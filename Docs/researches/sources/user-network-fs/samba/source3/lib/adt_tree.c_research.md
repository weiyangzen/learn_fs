# sources/user-network-fs/samba/source3/lib/adt_tree.c

Purpose: implements a small sorted path tree keyed by backslash-separated path components with inherited data pointers.

Important APIs/types/functions: private `struct tree_node` and `struct sorted_tree`; public `pathtree_init()`, `pathtree_add()`, `pathtree_find()`, `pathtree_print_keys()`; helper `trim_tree_keypath()`, `pathtree_birth_child()`, `pathtree_find_child()`, and recursive printing.

Control flow: `pathtree_add()` requires paths beginning with `\`, duplicates the path, splits it component by component, keeps children sorted by insertion shifting, and assigns `data_p` to the final node. `pathtree_find()` walks components and returns the deepest matching non-null data pointer, so parent policy/data applies to descendants until overridden.

State and persistence: the tree is entirely in-memory and talloc-owned; child arrays are reallocated under each node. It stores external `void *data_p` without owning or freeing that payload.

Dependencies/integration: uses talloc, Samba debug, `strcasecmp_m()` charset-aware comparison, `SMB_STRDUP`, and macros from `smb_macros.h`. Intended for consumers that need Windows-style path prefix matching.

Risks/test signals: no deletion API, linear child scan despite sorted storage, and mutation of duplicated path strings during parsing. Tests should cover root data inheritance, case-insensitive matching, insertion ordering, missing children, bad paths without leading backslash, allocation failure, and multiple descendants overriding parent data.
