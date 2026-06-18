# sources/storage-engines/wiredtiger/tools/tsan_playground/api_wt_acq_rel_barriers.h

Purpose: adapts the playground API to WiredTiger's acquire/release barrier macros plus relaxed WT atomic helpers.

Important APIs and control flow: includes `wt_internal.h`, defines plain `uint64_t` storage, uses `WT_RELEASE_BARRIER()` before `__wt_atomic_store_uint64_relaxed()`, and uses `__wt_atomic_load_uint64_relaxed()` followed by `WT_ACQUIRE_BARRIER()` for loads. `get_mode()` labels `WT acq/rel barriers`.

State and persistence behavior: in-memory shared counter synchronization only.

Dependencies and integration points: selected by `_WT_ACQ_REL_BARRIERS`; depends on WiredTiger internal headers and atomic macros from the build.

Risks: sanitizer recognition of WT barrier macros is the key uncertainty. The variant also depends on internal header include paths and macro definitions, so it is build-tree dependent.

Test signals: comparing its TSAN warnings to C11/GCC barrier variants indicates whether WT barrier macros are sanitizer-visible enough for this pattern.
