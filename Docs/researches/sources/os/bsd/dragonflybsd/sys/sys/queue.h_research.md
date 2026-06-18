# File Research: sources/os/bsd/dragonflybsd/sys/sys/queue.h

BSD intrusive linked-list and queue macro library.

Key responsibilities:
- Defines declarations and operations for:
  - `SLIST`: singly linked lists
  - `STAILQ`: singly linked tail queues
  - `LIST`: doubly linked forward lists
  - `TAILQ`: doubly linked tail queues
- Provides head/entry declarations, initializers, empty/first/next/prev/last accessors, foreach variants, mutable traversal variants, insertion, removal, concatenation, and swap macros.
- Provides optional `QUEUE_MACRO_DEBUG` trace storage and update macros.
- Provides kernel invariant checks for LIST and TAILQ link consistency.
- Trashes removed links under debug mode.

Important behavior:
- `SLIST`/`STAILQ` arbitrary removal is O(n); `LIST`/`TAILQ` arbitrary removal is O(1).
- `TAILQ` supports reverse traversal; `STAILQ` supports tail insertion with a last-next pointer.
- Debug and invariant macros add trace/check behavior without changing normal API names.

Dependencies:
- Includes `sys/cdefs.h` for helpers such as `__containerof`.

Notable risks:
- These macros evaluate arguments directly and require exact field names and initialized heads.
- Removing an element not in the expected list can corrupt memory; invariant checks help only when enabled.
- Intrusive list membership fields cannot safely be shared by multiple lists at once.
