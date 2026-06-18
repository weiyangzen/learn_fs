# sources/test-tools/kdevops/scripts/kconfig/list.h

## Purpose
This header implements a small subset of Linux kernel doubly linked list and hlist primitives for standalone Kconfig builds.

## Important APIs, Types, And Functions
It provides `container_of()`, list poison constants, `LIST_HEAD_INIT`, `LIST_HEAD`, `INIT_LIST_HEAD()`, `list_add()`, `list_add_tail()`, `list_del()`, `list_move()`, `list_move_tail()`, `list_is_head()`, `list_empty()`, entry accessors, forward/reverse/safe iteration macros, `HLIST_HEAD_INIT`, `hlist_add_head()`, `hlist_entry()`, `hlist_entry_safe()`, and `hlist_for_each_entry()`.

## Control Flow
All functions are static inline or macros. List insertion links a new node between known neighbors; deletion reconnects neighbors and poisons the deleted node; movement combines delete and insert. Iteration macros use `container_of()` to recover the parent object from embedded list nodes.

## State And Persistence
State is stored entirely in caller-owned embedded list nodes. There is no persistence and no allocation.

## Dependencies And Integration Points
It depends on `stddef.h`, compiler support for `typeof`, `_Static_assert`, and `__builtin_types_compatible_p`, plus `list_types.h`. Kconfig symbols, menus, properties, choices, and hash tables use these list primitives.

## Risks And Test Signals
The macros assume non-empty lists for first/last entry helpers and require nodes to be initialized. Poison values can expose use-after-delete in debugging but are not portable safety. Tests should exercise empty checks, insertion order, move order, safe deletion during iteration, hlist insertion/iteration, and compiler compatibility.
