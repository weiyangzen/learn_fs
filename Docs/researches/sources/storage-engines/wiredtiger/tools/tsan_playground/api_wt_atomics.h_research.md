# sources/storage-engines/wiredtiger/tools/tsan_playground/api_wt_atomics.h

Purpose: implements the playground API using WiredTiger's internal acquire/release uint64 atomic helpers.

Important APIs and control flow: `atomic_store_release()` calls `__wt_atomic_store_uint64_release()`, `atomic_load_acquire()` calls `__wt_atomic_load_uint64_acquire()`, and `get_mode()` returns `WT atomics`.

State and persistence behavior: in-memory counter synchronization only.

Dependencies and integration points: selected by `_WT_ATOMICS`; requires `wt_internal.h` and the repository's configured atomic abstraction.

Risks: this tests whether WT's native atomic helpers are both correct and visible to TSAN. It is not standalone outside a WiredTiger build.

Test signals: expected no TSAN data-race warnings if WT acquire/release helpers map to sanitizer-recognized operations.
