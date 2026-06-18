# sources/storage-engines/wiredtiger/tools/tsan_playground/api_c11_atomics.h

Purpose: implements the TSAN playground atomic API using native C11 acquire/release atomic operations.

Important APIs and control flow: defines `atomic_t`, `value_t`, `ATOMIC_DEFINE`, `atomic_store_release()` as `atomic_store_explicit(..., memory_order_release)`, `atomic_load_acquire()` as `atomic_load_explicit(..., memory_order_acquire)`, and `get_mode()`.

State and persistence behavior: only updates the shared counter used by the playground.

Dependencies and integration points: included by `tsan_playground.c` under `_C11_ATOMICS`; requires `<stdatomic.h>`.

Risks: this is the baseline standard-atomic implementation and should be TSAN-friendly. Portability risk is mainly compiler/library C11 atomic support.

Test signals: executable label is `C11 atomics`; expected runtime behavior is no data-race warning for the protected shared message/position accesses.
