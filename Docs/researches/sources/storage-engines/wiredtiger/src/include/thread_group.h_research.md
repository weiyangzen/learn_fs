# sources/storage-engines/wiredtiger/src/include/thread_group.h

Purpose: `thread_group.h` defines the shared control structures for WiredTiger utility thread pools such as eviction, checkpoint-adjacent workers, and other background services that need common start, pause, wake, and stop mechanics.

Important APIs and types: `WT_THREAD` stores a worker session, numeric id, OS thread id, lifecycle flags (`WT_THREAD_ACTIVE`, `WT_THREAD_CAN_WAIT`, `WT_THREAD_PANIC_FAIL`, `WT_THREAD_RUN`), a pause condition variable, and check/run/stop function pointers. `WT_THREAD_GROUP` stores allocation bounds, current active count, group name, a group lock, wake condition, an array of stable `WT_THREAD *` entries, and shared callbacks. `WT_THREAD_PAUSE` defines the paused-thread timeout.

Control flow: group owners allocate a `WT_THREAD_GROUP`, assign callbacks, and grow or shrink `WT_THREAD` entries. Individual threads call the check function to decide whether work is available, the run function to perform work, wait on `pause_cond` or `wait_cond` when inactive, and optionally call the stop function during teardown.

State and persistence behavior: all state is in-memory process/thread lifecycle state. The array is intentionally an array of pointers rather than structures so reallocating the group table does not move live thread contexts observed by running worker threads.

Dependencies and integration points: the definitions depend on `WT_SESSION_IMPL`, `WT_CONDVAR`, `WT_RWLOCK`, `wt_thread_t`, and WiredTiger flag macros. Thread-group management code and subsystem-specific background workers consume this header to share lifecycle semantics and panic-on-failure behavior.

Risks: lifetime and synchronization are central. Moving `WT_THREAD` objects, freeing a group while worker callbacks still reference it, or updating flags without the expected lock/condition discipline can race shutdown. Callback contracts are not type-rich, so subsystem implementations must preserve session ownership and blocking rules themselves.

Test signals: background-worker start/stop tests, resize tests that grow and shrink groups under load, shutdown/panic injection for `WT_THREAD_PANIC_FAIL`, condition wake tests for paused workers, and sanitizer runs that exercise worker teardown while work remains queued.
