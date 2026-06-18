# sources/storage-engines/wiredtiger/tools/tsan_playground/api_c11_acq_rel_barriers.h

Purpose: implements the TSAN playground atomic API using C11 relaxed load/store plus separate acquire/release fences.

Important APIs and control flow: defines `atomic_t` as `atomic_uint_fast64_t`, `value_t` as `uint64_t`, `ATOMIC_DEFINE`, `atomic_store_release()` with `atomic_thread_fence(memory_order_release)` followed by relaxed store, `atomic_load_acquire()` with relaxed load followed by acquire fence, and `get_mode()`.

State and persistence behavior: only manipulates caller-provided atomic variables in memory.

Dependencies and integration points: included by `tsan_playground.c` when `_C11_ACQ_REL_BARRIERS` is defined. Requires C11 `<stdatomic.h>`.

Risks: fence-plus-relaxed patterns are exactly what the playground is meant to study; TSAN may not model them the same as acquire/release atomics. `atomic_uint_fast64_t` may not be exactly 64 bits on all platforms, though values are used as counters.

Test signals: executable should print `Implementation: C11 acq/rel barriers`; TSAN warnings collected by `collect_warnings.sh` indicate whether this synchronization is recognized.
