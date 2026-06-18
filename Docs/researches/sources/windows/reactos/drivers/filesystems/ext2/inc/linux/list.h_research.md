# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/list.h

This header implements the classic Linux intrusive doubly linked list API.

Provided elements:
- `struct list_head`
- `LIST_HEAD_INIT`, `LIST_HEAD`, `INIT_LIST_HEAD`
- Internal add/delete helpers: `__list_add`, `__list_del`, `__list_splice`
- Operations: `list_add`, `list_add_tail`, `list_del`, `list_del_init`, `list_move`, `list_move_tail`, `list_empty`, `list_empty_careful`, `list_splice`, `list_splice_init`
- Container/iteration macros: `list_entry`, `list_for_each`, `list_for_each_safe`, `list_for_each_prev`, `list_for_each_entry`, `list_for_each_entry_safe`
- `prefetch(a)` stub.

Role:
- Supports Linux-derived structures such as orphan lists, xattr ordered lists, and other compatibility containers.

Notable constraints:
- No debug poisoning, validation, or concurrency protection is provided.
- Iteration macros use the local `prefetch` no-op/stub.
