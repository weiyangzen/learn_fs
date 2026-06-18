# sources/test-tools/stress-ng/core-pthread.h

Purpose: provides the small pthread-facing portability surface used by stressors that run helper threads or need a low-overhead lock abstraction. It depends on `stress_args_t` and the generated feature macros from `stress-ng.h`.

Important APIs/types/functions: `stress_pthread_args_t` packages a stressor argument pointer, per-thread private data, and a return code. `shim_pthread_spinlock_t` aliases either `pthread_spinlock_t` or `pthread_mutex_t`. The `shim_pthread_spin_*` macros map lock, unlock, init, and destroy operations to the selected primitive, while `SHIM_PTHREAD_PROCESS_SHARED/PRIVATE` track the compatible initializer argument.

Control flow: this is header-only. Compile-time feature checks choose real spinlocks when libpthread and spinlock support are present, excluding platforms called out as problematic, otherwise a mutex-backed implementation is selected.

State and persistence: no owned persistent state. Users own the lock object and any `stress_pthread_args_t` storage.

Dependencies/integration: used by resource allocation and stressors that need pthread wrappers without repeating platform guards. Risk is mostly semantic drift: the mutex fallback does not have spinlock performance or the same process-shared behavior, because the fallback shared/private macros are `NULL`.

Test signals: build matrix coverage across Linux/BSD-like pthread variants, plus stressors that initialize, lock, unlock, and destroy shim locks. Watch for compile failures when pthread feature macros are inconsistent.
