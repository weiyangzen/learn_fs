# sources/storage-engines/wiredtiger/tools/tsan_playground/api_wt_store_load_with_barriers.h

Purpose: implements the playground API with WiredTiger combined store/load barrier macros rather than explicit relaxed atomics plus separate barriers.

Important APIs and control flow: `atomic_store_release()` uses `WT_RELEASE_WRITE_WITH_BARRIER(*var, value)`. `atomic_load_acquire()` uses `WT_ACQUIRE_READ_WITH_BARRIER(result, *var)` and returns the loaded value. `get_mode()` currently returns the same `WT acq/rel barriers` label as another variant.

State and persistence behavior: mutates caller-provided in-memory counter state.

Dependencies and integration points: selected by `_WT_STORE_LOAD_WITH_BARRIERS`; depends on WT internal macros from `wt_internal.h`.

Risks: duplicate `get_mode()` label can make `collect_warnings.sh` output ambiguous between this target and `api_wt_acq_rel_barriers.h`. Correctness depends on macro expansion and sanitizer visibility.

Test signals: target-specific executable name plus collected TSAN summaries are needed because the printed implementation label is not unique.
