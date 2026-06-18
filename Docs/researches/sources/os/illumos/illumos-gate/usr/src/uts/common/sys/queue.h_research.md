# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/queue.h

## Role

`queue.h` is the BSD queue macro collection adapted for illumos. It provides intrusive container macros for singly-linked lists, singly-linked tail queues, lists, simple queues, tail queues, and compatibility circular queues.

## Families

The header defines:
- `SLIST_*`: singly-linked lists, forward traversal, O(n) arbitrary removal.
- `STAILQ_*`: singly-linked tail queues with O(1) tail insert.
- `LIST_*`: doubly-linked forward lists using previous-next pointers.
- `SIMPLEQ_*`: simple queues with first and last-next pointers.
- `TAILQ_*`: doubly-linked tail queues with forward/reverse traversal and O(1) insertion/removal.
- `CIRCLEQ_*`: circular queues retained for compatibility but explicitly discouraged due to pointer-aliasing issues.

Each family has head/entry declarations, class-friendly C++ variants where applicable, initializers, accessors, traversal macros, safe traversal variants, insertion/removal, concatenation or swapping as relevant.

## Debug Facilities

Optional debug support includes:
- `QUEUE_MACRO_DEBUG_TRACE`: stores last two mutation sites in `qm_trace`.
- `QUEUE_MACRO_DEBUG_TRASH`: poisons removed links with `(void *)-1`.
- Kernel `QUEUEDEBUG` assertions for `LIST_*` and `TAILQ_*` integrity.

The file also includes `sys/containerof.h` for previous-element derivation macros such as `STAILQ_LAST()` and `LIST_PREV()`.

## Notable Details

`QUEUE_TYPEOF()` handles C++ class lists. `_NOTE(CONSTCOND)` annotations support lint/warlock expectations around macro loops. Some macros assume valid membership and do not guard against missing elements; callers must maintain list invariants.

## Research Notes

This is foundational infrastructure used across many kernel and userland components. The most important behavior is macro side-effect safety and invariant preservation for intrusive links; changing field semantics or debug poisoning would have broad impact.
