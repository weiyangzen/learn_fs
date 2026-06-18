# sources/user-network-fs/nfs-ganesha/src/include/gsh_list.h

Purpose: This header provides Ganesha's intrusive doubly linked list primitives and `container_of` helper.

Important APIs/types/functions: `struct glist_head` is the embedded node/head. Initialization macros/functions include `GLIST_HEAD_INIT`, `GLIST_HEAD`, and `glist_init`. Mutation helpers include `glist_add`, `glist_add_tail`, `glist_del`, `glist_move_tail`, `glist_add_list_tail`, `glist_splice_tail`, `glist_swap_lists`, `glist_split`, and `glist_insert_sorted`. Iteration and container helpers include `glist_for_each`, safe variants, `glist_first_entry`, `glist_last_entry`, `glist_entry`, next/previous entry macros, and `glist_length`.

Control flow: Callers embed `glist_head` in owner structs, initialize heads to self-pointing empty lists, splice/move/delete nodes, and recover owners through `container_of`.

State and persistence: List state is purely in-memory. Deleted nodes are poisoned with NULL next/prev so `glist_null` can identify unlinked nodes.

Dependencies and integration points: Used throughout FSAL module/export/object lists, DBus broadcast queues, hash/FD LRU users, and many daemon collections. No locking is provided; callers must synchronize.

Risks: Adding an already-linked node corrupts lists. Using list operations without caller-held locks races. `glist_split` assumes a non-empty source and empty destination. `container_of` relies on GNU `typeof`.

Test signals: Unit-test empty/non-empty insert/delete/splice/swap/split cases, safe deletion during iteration, sorted insertion ordering, node poisoning, and list length after each mutation.
