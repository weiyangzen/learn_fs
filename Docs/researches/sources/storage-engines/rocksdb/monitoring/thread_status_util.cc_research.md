# sources/storage-engines/rocksdb/monitoring/thread_status_util.cc

Purpose: Implements static convenience wrappers for thread-status tracking, caching the current Env's `ThreadStatusUpdater` in thread-local state.

Important APIs/types/functions: Implements `RegisterThread`, `UnregisterThread`, `SetEnableTracking`, `SetColumnFamily`, `SetThreadOperation`, `GetThreadOperation`, `SetThreadOperationStage`, operation property setters, `SetThreadState`, `ResetThreadStatus`, CF metadata creation/erasure, `MaybeInitThreadLocalUpdater`, and `AutoThreadOperationStageUpdater`.

Control flow: The first non-unregister call can initialize the thread-local updater from an Env. Registration records thread type and Env thread ID. Operation setting records start time for non-unknown operations and clears it for unknown. The RAII stage updater stores the previous stage in its constructor and restores it in the destructor.

State and dependencies: Uses thread-local `thread_updater_initialized_` and `thread_updater_local_cache_`; disabled builds use static no-op variables/functions. Depends on Env, SystemClock, and `ThreadStatusUpdater`.

Risks/test signals: The first Env used by a thread wins until `UnregisterThread`, so mixed-Env threads must unregister to switch updater caches. Some methods require prior initialization and silently no-op otherwise. Debug hooks are declared elsewhere.
