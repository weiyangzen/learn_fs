<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/list.h -->
# sources/test-tools/strace/src/list.h

Purpose: small intrusive doubly linked-list utility modeled after Linux kernel lists.
Important APIs/types/functions: `struct list_item`, `EMPTY_LIST`, `list_init`, `list_is_empty`, `list_elem`, head/tail/next/prev macros, insert/append/remove/replace helpers, and iteration macros.
Control flow: inline helpers splice circular list links and reset removed/replaced nodes to self-links. `list_is_empty` also treats zeroed uninitialized nodes as empty.
State and persistence behavior: mutates caller-owned embedded list nodes; no allocation. Dependencies and integration points: depends on `containerof` from `macros.h` and is reused by internal strace collections.
Risks: macros assume valid embedded fields and are not thread-safe. Test signals: unit-style insertion/removal/iteration tests, including removal while iterating.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/list.h -->
