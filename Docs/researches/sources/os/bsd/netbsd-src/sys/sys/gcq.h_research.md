# File Research: sources/os/bsd/netbsd-src/sys/sys/gcq.h

Read completely: 463 lines.

## Purpose
Implements generic intrusive circular queues with inline operations, merge support, typed container recovery, and traversal/dequeue macros.

## Main Interfaces
- Structures: `struct gcq`, `struct gcq_head`.
- Initializers: `GCQ_INIT`, `GCQ_INIT_HEAD`, `gcq_init`, `gcq_init_head`.
- State helpers: `gcq_onlist`, `gcq_empty`, `gcq_linked`.
- Insertion/removal/merge: `gcq_insert_after`, `gcq_insert_before`, `gcq_insert_head`, `gcq_insert_tail`, `gcq_tie`, `gcq_merge`, `gcq_remove`, `gcq_clear`, `gcq_remove_all`.
- Container macro: `GCQ_ITEM`.
- Dequeue/get macros for first/last/next/prev, typed and conditional variants.
- Iteration macros: `GCQ_FOREACH*`, reverse, safe-next, read-only, dequeueing, typed variants.
- Search macros: `GCQ_FIND*`.

## Dependencies And Integration
Usable in kernel or userland testing; depends on assertion support and standard integer/offset types. Generic infrastructure for subsystems needing intrusive queues.

## Risks And Edge Cases
- Items must be initialized before insertion; assertions check self-linked state.
- Traversal after removal requires correct safe iteration macros.
- Some conditional helper macros reference `fn`/`var` in ways that look fragile or possibly erroneous.
- `GCQ_FOREACH_RO_TYPED` uses `gcq_lined`, likely a typo for `gcq_linked`.

## Filesystem Relevance
Indirect. Generic kernel data-structure support that filesystem/block code could use.
