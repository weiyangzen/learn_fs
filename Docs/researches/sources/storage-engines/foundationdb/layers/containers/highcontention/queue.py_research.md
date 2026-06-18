# sources/storage-engines/foundationdb/layers/containers/highcontention/queue.py

Purpose: This file implements a FoundationDB queue layer with an optional high-contention pop algorithm. The default mode trades isolated pop latency for better scaling when many clients pop concurrently.

Important APIs and types: `Subspace` provides tuple prefix helpers. `Queue` exposes `clear`, `push`, `pop`, `empty`, and `peek`; private helpers manage `item`, `pop`, and `conflict` subspaces. Values are tuple-packed, queue entries are keyed by `(index, randomID)`, and waiting pop requests are keyed with random IDs.

Control flow: `push` computes the next index from a snapshot read and writes an item with a random suffix. Simple pop reads and deletes the first item in one transaction. High-contention pop first registers behind existing waiters if needed, then repeatedly fulfills waiting pops in batches by moving item values to per-waiter result keys and polling its own result key with exponential backoff.

State and persistence behavior: Persistent state includes queued items, pending pop requests, and fulfilled-result keys. The `active` conflict behavior is encoded through reads of wait and item keys. Pop cannot be composed with arbitrary caller transactions because the high-contention path spans multiple transactions and polling.

Dependencies and integration points: It uses `fdb.api_version(22)`, tuple subspaces, `os.urandom`, Python `threading` examples, and FDB transaction retry semantics. Example functions demonstrate single-client and multi-client queue usage.

Risks: Random ID uniqueness depends on OS entropy. The high-contention code has a questionable exception path that calls transactional `_addConflictedPop(db, True)` after a failed manual transaction, and polling can leave result keys if clients exit. Tests should cover FIFO-ish behavior under same-index randomization, empty pop, waiter fulfillment, concurrent producers/consumers, cleanup of abandoned waits, and retry handling.
