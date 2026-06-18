# sources/security-integrity/audit-userspace/audisp/queue.h

Purpose: Defines the public hidden-symbol interface for audisp's dispatcher queue implementation.

Important APIs, types, and functions: Declares queue mode flags `Q_IN_MEMORY`, `Q_IN_FILE`, `Q_CREAT`, `Q_EXCL`, `Q_SYNC`, and `Q_RESIZE`. Exposes lifecycle, producer/consumer, resize, state dump, resume, and metric functions for `event_t *` queues. It includes `dso.h` and wraps declarations in `AUDIT_HIDDEN_START/END`.

Control flow: The header establishes expected call ordering: initialize, enqueue/dequeue events, optionally nudge or resize, dump state/resume as needed, and destroy. `dequeue_timed()` exposes timed waiting for tests or nonblocking dispatcher patterns.

State and persistence: No state is declared in the header; the implementation uses one global queue. Flags specify whether to use memory only or a file-backed persistent queue and whether file writes should be synchronous.

Dependencies and integration points: Coupled to `event_t` from `libdisp.h` and dispatcher configuration from `audispd-config.h`. It is linked into `libqueue.la` and tested by `audisp-queue-test`.

Risks and edge cases: The queue API transfers ownership of `event_t *` to `enqueue()` even on failure paths that free the event. Callers must not reuse an event after enqueue returns nonzero. Because there is no queue handle, concurrent independent queues cannot be represented.

Test signals: `test-queue.c` is the direct consumer. Build integration is in `audisp/test/Makefile.am`, where `audisp-queue-test` links `libqueue.la` and `libaucommon.la`.
