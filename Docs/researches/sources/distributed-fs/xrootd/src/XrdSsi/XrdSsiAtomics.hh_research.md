# sources/distributed-fs/xrootd/src/XrdSsi/XrdSsiAtomics.hh

## Purpose
Provides SSI portability macros for atomic counters/flags and lightweight mutex RAII helpers.

## Important APIs, Types, And Functions
- `Atomic(type)` and operations `Atomic_INC`, `Atomic_DEC`, `Atomic_GET`, `Atomic_GET_STRICT`, `Atomic_SET`, `Atomic_SET_STRICT`, and `Atomic_ZAP`.
- Implementation selector `Atomic_IMP` chooses C++11 atomics, GCC `__atomic`, GCC `__sync`, or a mutex-required fallback.
- `XrdSsiMutex` wraps `pthread_mutex_t` with simple or recursive construction.
- `XrdSsiMutexMon` is an RAII monitor that can lock, switch, reset, and unlock an `XrdSsiMutex`.

## Control Flow
At compile time the header selects one atomic implementation. C++11 uses relaxed operations by default and acquire/release for strict get/set. Legacy GCC paths use builtin atomics. The fallback defines `NEED_ATOMIC_MUTEX` and wraps ordinary operations in caller-provided mutex lock/unlock macros. `XrdSsiMutexMon` locks on construction when provided a mutex and unlocks on destruction.

## State And Persistence
Macros operate on caller-owned variables. Mutex classes own a `pthread_mutex_t` and release it in the destructor. No persistence beyond process synchronization state.

## Dependencies And Integration Points
Used throughout SSI for global counters and init flags, including `XrdSsiClient.cc`. Depends on pthreads and optionally C++ `<atomic>`. `XrdSsiAtomics.cc` supplies error text conversion.

## Risks And Edge Cases
- Relaxed memory order is used for most operations; only strict variants carry acquire/release semantics.
- Fallback macro set lacks `Atomic_GET_STRICT` and `Atomic_SET_STRICT` definitions, which can break code if fallback is active.
- `Atomic_DEC` and `Atomic_INC` return the pre-operation value for C++ and GCC builtins, not the new value; callers must know the convention.
- The mutex constructor throws a `const char *`, which is unusual for C++ exception handling.

## Test Signals
Build tests across C++11 and legacy atomic configurations, concurrency tests for init flags and counters, recursive mutex behavior, RAII lock switching in `XrdSsiMutexMon`, and fallback build validation if atomics are disabled.
