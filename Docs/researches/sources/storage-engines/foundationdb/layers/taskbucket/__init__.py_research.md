# sources/storage-engines/foundationdb/layers/taskbucket/__init__.py

Purpose: This package implements a FoundationDB TaskBucket layer for distributed task queues plus a Future/FutureBucket mechanism for dependency tracking and callbacks. It lets multiple clients claim tasks, run them, finish them, and requeue timed-out work.

Important APIs and types: `Subspace`, `TaskTimedOutException`, `TaskBucket`, `TaskDispatcher`, `FutureBucket`, and `Future` are the main public types. `TaskBucket` exposes `clear`, `add`, `addIdle`, `get_one`, `is_empty`, `is_busy`, `finish`, `is_finished`, `check_active`, `extend`, and `check_timeouts`. `TaskDispatcher` registers task functions and dispatches dictionaries; `Future` supports `is_set`, `on_set_add_task`, `on_set`, `set`, `join`, and `joined_future`.

Control flow: `TaskBucket.add` writes task dictionary fields under `available`. `get_one` chooses a random-ish available task by snapshot key selector, moves fields into `timeouts` under a read-version-based timeout, deletes the available record, and returns task metadata. `finish` deletes timeout records or raises if they already expired. `check_timeouts` scans expired timeout records and restores them to available. Futures store block keys; setting a future clears blocks and performs stored callback task dictionaries through the dispatcher.

State and persistence behavior: Persistent task state is split into available tasks, timeout/lock records, an active marker, future block records, and future callback records. Task dictionaries are stored field-by-field and may include packed custom values. System-key access can be enabled for special deployments.

Dependencies and integration points: It uses `fdb.api_version(200)`, UUID random keys, tuple subspaces, read versions as timeout clocks, and transaction options for system keys. It integrates with user-defined Python functions through `TaskDispatcher.taskType`.

Risks: `extend` is unimplemented, and `TaskDispatcher.do_one` dispatches but does not call `finish`; task functions must finish themselves or tasks remain locked until timeout. Timeout math depends on read versions and a configured millisecond-like value. Tests should cover claim/finish/requeue, idle tasks, timeout exceptions, future joins/callbacks, system-key options, and task functions that fail before finishing.
