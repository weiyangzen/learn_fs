# File Research: sources/local-fs/dlm/dlm_controld/list.h

This is a userspace copy of Linux `include/linux/list.h`, backed by helpers from `linux_helpers.h`. It provides intrusive circular doubly linked list primitives used throughout `dlm_controld`.

Covered functionality:
- List declaration and initialization: `struct list_head`, `LIST_HEAD_INIT`, `LIST_HEAD`, `INIT_LIST_HEAD`.
- Add/delete/move/replace/swap operations: `list_add`, `list_add_tail`, `list_del`, `list_del_init`, `list_move`, `list_move_tail`, `list_replace`, `list_replace_init`, `list_swap`.
- Bulk and splice operations: `list_bulk_move_tail`, `list_cut_position`, `list_cut_before`, `list_splice`, `list_splice_tail`, `list_splice_init`, `list_splice_tail_init`.
- State predicates: `list_empty`, `list_is_first`, `list_is_last`, `list_is_head`, `list_is_singular`.
- Entry helpers: `list_entry`, first/last/or-null helpers, next/prev helpers, circular next/prev helpers.
- Iteration macros: raw list iteration, reverse iteration, safe iteration, typed entry iteration, continuation/from/reverse variants, and safe variants.
- `list_count_nodes()` counts entries in a list.

Used heavily by:
- Lockspace lists and run-operation lists in `main.c`.
- Cluster node tracking in `member.c`.
- Plock resource, lock, waiter, pending, and saved-message lists in `plock.c`.
- Other daemon modules outside this group.

Notable details:
- Debug list validation hooks are stubbed out unless `CONFIG_DEBUG_LIST` is defined.
- Deleted entries are poisoned, which helps catch accidental reuse.
- Because it is intrusive, lifetime management is entirely the caller’s responsibility.
