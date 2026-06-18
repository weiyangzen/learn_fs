# File Research: sources/local-fs/ocfs2-tools/ocfs2console/blkid/list.h

Local copy of a Linux-kernel-style intrusive doubly linked list implementation.

Key contents:
- `struct list_head`
- Initialization macros:
  - `LIST_HEAD_INIT`
  - `LIST_HEAD`
  - `INIT_LIST_HEAD`
- Operations:
  - `list_add`
  - `list_add_tail`
  - `list_del`
  - `list_del_init`
  - `list_empty`
  - `list_splice`
- Iteration and container macros:
  - `list_entry`
  - `list_for_each`
  - `list_for_each_safe`

Usage:
- Used by all bundled blkid cache/device/tag structures.

Notable details:
- Header guard also checks `LIST_HEAD`, avoiding collision with system queue/list headers.
- The implementation trades type safety for compact intrusive list manipulation.
