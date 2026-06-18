# sources/storage-engines/wiredtiger/tools/tsan_playground/api_dummy.h

Purpose: intentionally unsynchronized implementation of the playground atomic API, used as a negative control.

Important APIs and control flow: defines `atomic_t` and `value_t` as plain `uint64_t`, `ATOMIC_DEFINE` as a static plain variable, `atomic_store_release()` as `*var = value`, `atomic_load_acquire()` as `return *var`, and `get_mode()`.

State and persistence behavior: mutates shared memory without atomics or barriers.

Dependencies and integration points: selected by `_DUMMY_ATOMICS` or as the fallback include for editor parsing before the compile-time `#error` in `tsan_playground.c`.

Risks: it intentionally contains data races and should not be used as a synchronization template.

Test signals: TSAN should report warnings for the dummy executable; absence of warnings would indicate the playground or sanitizer setup is ineffective.
