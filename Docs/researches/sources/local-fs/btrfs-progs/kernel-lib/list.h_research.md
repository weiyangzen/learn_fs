# File Research: sources/local-fs/btrfs-progs/kernel-lib/list.h

## Purpose
Userspace copy/adaptation of Linux intrusive doubly-linked list and hlist primitives.

## Key Interfaces
- `struct list_head`, `struct hlist_head`, `struct hlist_node`.
- Initialization macros/functions: `LIST_HEAD_INIT`, `LIST_HEAD`, `INIT_LIST_HEAD`, `HLIST_HEAD`, `INIT_HLIST_HEAD`, `INIT_HLIST_NODE`.
- List mutation: `list_add`, `list_add_tail`, `list_del`, `list_del_init`, `list_replace`, `list_swap`, `list_move`, `list_bulk_move_tail`, splice/cut helpers.
- List queries: `list_empty`, `list_empty_careful`, `list_is_first`, `list_is_last`, `list_is_singular`.
- Typed entry and iteration macros, including safe variants for deletion during iteration.
- Hlist mutation/query/iteration helpers.

## Dependencies
Includes `kerncompat.h`, `<stddef.h>`, and `<stdbool.h>`. Uses `container_of`, `READ_ONCE`, `WRITE_ONCE`, and optional debug validation hooks.

## Notable Behaviors
- Poison pointers are assigned after destructive deletion to catch misuse.
- `list_empty_careful()` uses acquire/release-style wrappers for the limited synchronization pattern documented in the file.
- Hlist nodes track predecessor link by pointer-to-pointer, enabling O(1) deletion without a full doubly linked head.

## Risks
- These primitives do not own storage or enforce lifetime; use-after-free and double deletion remain caller responsibilities.
- Debug validation is compiled out unless `CONFIG_DEBUG_LIST` is provided.
- Concurrency safety is minimal and mirrors the comments: most use requires external locking.
