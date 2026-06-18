# sources/security-integrity/audit-userspace/audisp/plugins/remote/queue.h

Purpose: declares the audisp-remote queue abstraction and storage flags.

Important APIs and data: opaque `struct queue`; flags `Q_IN_MEMORY`, `Q_IN_FILE`, `Q_CREAT`, `Q_EXCL`, `Q_SYNC`, and `Q_RESIZE`; `QUEUE_ENTRY_SIZE` is 3*4096; public open/close/append/peek/drop/length functions.

Control flow: callers configure storage and durability behavior via flags at `q_open`.

State and persistence: file-backed queues persist when `Q_IN_FILE` is set; memory-only queues do not.

Dependencies and integration: includes common attribute macros and is used by `audisp-remote.c` and `test-queue.c`.

Risks: comments say `q_peek` returns 1 for an entry, but implementation returns the entry byte length; callers should treat positive values as length.

Test signals: `test-queue.c` validates the public API contract.
