# sources/storage-engines/wiredtiger/tools/tsan_playground/api_wt_full_barriers.h

Purpose: implements the playground API using WiredTiger full barriers around relaxed WT atomic accesses.

Important APIs and control flow: `atomic_store_release()` calls `WT_FULL_BARRIER()` then `__wt_atomic_store_uint64_relaxed()`. `atomic_load_acquire()` uses relaxed load then `WT_FULL_BARRIER()`. `get_mode()` labels the variant.

State and persistence behavior: in-memory synchronization wrapper only.

Dependencies and integration points: selected by `_WT_FULL_BARRIERS`; depends on WT internal barrier and atomic macros.

Risks: like the other fence variants, architectural ordering and TSAN modeling may diverge. Full barriers can also be more expensive than necessary if used as a production pattern.

Test signals: `collect_warnings.sh` shows whether TSAN accepts this WT full-barrier pattern or reports races.
