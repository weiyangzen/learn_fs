# sources/user-network-fs/nfs-utils/utils/idmapd/queue.h

Purpose: local copy of BSD queue macros used by idmapd for intrusive lists, especially `TAILQ` client tracking.

Important APIs and types: the header defines `SLIST`, `LIST`, `SIMPLEQ`, `TAILQ`, and `CIRCLEQ` head/entry/access/manipulation macros. `idmapd.c` uses `TAILQ_HEAD`, `TAILQ_ENTRY`, `TAILQ_INIT`, `TAILQ_FOREACH`, `TAILQ_INSERT_TAIL`, `TAILQ_REMOVE`, `TAILQ_FIRST`, and `TAILQ_NEXT`.

Control flow: macros perform pointer manipulation inline in callers. Tail queues provide O(1) insertion/removal and forward traversal for active idmap clients.

State and persistence: no standalone state; list membership is embedded in consumer structs. Persistence is in process memory only.

Dependencies and integration: avoids dependency on platform `<sys/queue.h>` semantics by shipping an older BSD-compatible implementation.

Risks: macros are type-unsafe and evaluate arguments in pointer-heavy contexts; misuse can corrupt list links. The circular queue `CIRCLEQ_REPLACE` macros reference `head` inconsistently with pointer-style usage, but idmapd does not use them. Test signals are compile coverage and dynamic add/remove/rescan client behavior that exercises the TAILQ subset.
