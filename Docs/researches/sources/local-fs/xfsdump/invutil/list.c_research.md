# File Research: sources/local-fs/xfsdump/invutil/list.c

Implements a doubly linked list plus parent/child relationships for the ncurses inventory menu.

Core behavior:
- `node_create()` allocates a `node_t` and `data_t`, initializing visibility, expansion, delete/import/commit state, file/data indexes, displayed text, operation table, parent, and children.
- `list_add()` inserts after a previous node and registers the new node as a child of its parent.
- `list_del()` detaches a node from the list.
- `free_all_children()` recursively frees descendants.
- `mark_all_children_commited()` marks a subtree as committed after a parent operation is written to inventory state.

Notable details:
- Deleted nodes have their displayed text first byte set to `D`.
- `parent_add_child()` grows the child pointer array with `realloc`.
- `node_free()` frees text, children array, data, and node.

Risks:
- `node_create()` leaks `newnode` if `newdata` allocation fails.
- `parent_add_child()` does not handle `realloc` failure.
- Ownership is manual: display text and child arrays are freed by node cleanup, but payload data referenced by `data_idx` is managed elsewhere.
