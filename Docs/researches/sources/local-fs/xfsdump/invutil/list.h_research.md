# File Research: sources/local-fs/xfsdump/invutil/list.h

Declares the menu list abstraction used by `invutil`.

Key types:
- `node_t`: doubly linked list node with opaque `data`.
- `data_t`: menu metadata, including indentation level, hidden/expanded/deleted/imported/committed flags, file index, display text, operation table, parent/children, child count, and data index into mmap-backed file records.

Exports list and node helpers:
- `node_create`, `node_free`
- `list_add`, `list_del`
- `free_all_children`
- `mark_all_children_commited`

Role:
- Provides the common tree/list model used by menu rendering, storage-object menus, and commit/delete operations.
