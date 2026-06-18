# sources/storage-engines/wiredtiger/tools/tsan_playground/api_c11_full_barriers.h

Purpose: implements the TSAN playground atomic API using C11 sequentially consistent fences around relaxed access.

Important APIs and control flow: `atomic_store_release()` issues `atomic_thread_fence(memory_order_seq_cst)` then relaxed store. `atomic_load_acquire()` performs relaxed load then seq-cst fence. `get_mode()` returns `C11 full barriers`.

State and persistence behavior: in-memory synchronization wrapper only.

Dependencies and integration points: selected by `_C11_FULL_BARRIERS` in `tsan_playground.c`; requires C11 atomics.

Risks: full fences may be stronger architecturally but still may not create a TSAN-recognized synchronization relation around relaxed accesses. Runtime warnings are the point of this variant.

Test signals: build plus `collect_warnings.sh` output identifies whether TSAN reports races for this barrier style.
