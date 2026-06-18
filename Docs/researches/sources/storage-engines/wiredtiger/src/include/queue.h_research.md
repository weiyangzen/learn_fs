# sources/storage-engines/wiredtiger/src/include/queue.h

## Purpose
Provides a WiredTiger-local, stripped-down FreeBSD `sys/queue.h` implementation for tail queues (`TAILQ`) with compatibility undefines to avoid conflicts with system or Windows headers.

## Important APIs, Types, And Functions
- Undefines existing `TAILQ_*`, trace, and queue helper macros before defining WiredTiger's versions.
- `TAILQ_HEAD`, `TAILQ_CLASS_HEAD`, `TAILQ_ENTRY`, and `TAILQ_CLASS_ENTRY` declare queue heads and links.
- Iteration macros include forward/reverse and safe variants.
- Mutation macros include `TAILQ_INIT`, `TAILQ_INSERT_HEAD`, `TAILQ_INSERT_TAIL`, `TAILQ_INSERT_AFTER`, `TAILQ_INSERT_BEFORE`, `TAILQ_REMOVE`, `TAILQ_CONCAT`, and `TAILQ_SWAP`.
- Access macros include `TAILQ_EMPTY`, `TAILQ_FIRST`, `TAILQ_LAST`, `TAILQ_NEXT`, and `TAILQ_PREV`.

## Control Flow
TAILQ heads maintain first element and pointer-to-last-next. Insertions update neighboring `tqe_prev` pointers and the head's tail pointer. Removal repairs either the next element's previous pointer or the head tail pointer, then patches the previous next pointer. Safe iteration variants precompute the next/previous element before the body runs.

## State And Persistence Behavior
Queue links are in-memory intrusive list state embedded in owning structures. No persistent data is encoded directly, but queues organize persistent-resource handles, sessions, work units, and metadata objects.

## Dependencies And Integration Points
Self-contained apart from C/C++ type syntax. Used broadly by file-handle queues, session handle caches, cursors, RTS work queues, schema structures, and many internal lists.

## Risks
Intrusive macros do no runtime validation in this stripped version; double insert/remove or wrong field/head type can corrupt memory. Because all conflict macros are undefined, including this header intentionally overrides platform definitions. C++ class variants must be used for class types.

## Test Signals
Unit tests or sanitizer tests should cover insert/remove at head/tail/middle, concat, swap, safe iteration while removing elements, empty queues, C++ class entries, and misuse detection under debug instrumentation where available.
