# sources/storage-engines/tikv/components/tikv_util/src/sys/thread.rs

## Purpose
Provides unified process/thread ID, thread CPU stat, thread priority, thread-name tracking, and thread-start/stop hook integration across standard threads, Tokio runtimes, and futures thread pools.

## Important APIs, Types, and Functions
- `ThreadStat { s_time, u_time }` and `total_cpu_time`.
- Platform exports from `imp`: `Pid`, `FullStat`, `ticks_per_second`, `process_id`, `thread_id`, `thread_ids`, `full_thread_stat`, `set_priority`, and `get_priority`.
- `thread_stat` and `current_thread_stat`.
- `StdThreadBuildWrapper::spawn_wrapper` and `ThreadBuildWrapper::{with_sys_and_custom_hooks,with_sys_hooks}`.
- Globals: `THREAD_NAME_HASHMAP` and `THREAD_START_HOOKS`.
- Hook helpers: `hook_thread_start`, `call_thread_start_hooks`, `add_thread_name_to_map`, `remove_thread_name_from_map`.

## Control Flow
Linux thread IDs come from cached process ID and thread-local `SYS_gettid`; thread lists read `/proc/<pid>/task`. Full stats use `procinfo::pid::stat_task`, and priority uses `setpriority/getpriority` after clearing errno for `getpriority`. Wrapped thread builders install common start hooks: call registered start hooks, add allocator memory accessor, allocate an exclusive arena, record thread name, run custom start hook, and on stop remove name/accessor plus custom end hook.

## State and Persistence Behavior
Thread-name and start-hook registries are process-global mutex-protected maps/vectors. Thread IDs are cached per thread on Linux. Allocator memory accessors are registered for thread lifetime and removed on stop. No durable state exists.

## Dependencies and Integration Points
Depends on `tikv_alloc` thread memory APIs, `collections::HashMap`, `defer`, `libc`/platform APIs, Tokio runtime builder hooks, futures `ThreadPoolBuilder`, and TiKV Yatp tests. Metrics code uses `THREAD_NAME_HASHMAP` to label per-thread metrics.

## Risks
The global hook vector grows monotonically; no unregister API exists. Builder wrappers must be used consistently or thread metrics/allocation tracking will be incomplete. Comments note a potential issue if a user only calls an after-start wrapper without before-stop cleanup in external APIs. Non-Linux implementations are best-effort stubs.

## Test Signals
Tests verify nonzero/different thread IDs, thread list membership while threads are alive and absence after stop, Linux priority set/get behavior with permission handling, and thread-name tracking across std thread wrapper, Yatp future pool, and Tokio builder hooks.
