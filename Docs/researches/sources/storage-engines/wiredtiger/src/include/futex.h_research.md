## sources/storage-engines/wiredtiger/src/include/futex.h

Purpose: this header defines the tiny shared type contract for WiredTiger's futex-style synchronization API. The comment explicitly says the futex API is for building other synchronization mechanisms and is not intended for general use.

Important APIs/types/functions: `WT_FUTEX_WORD` is a `uint32_t`, matching Linux's futex word-size limit even on 64-bit architectures. `WT_FUTEX_WAKE` is an enum with `WT_FUTEX_WAKE_ONE` and `WT_FUTEX_WAKE_ALL`, controlling whether wake operations release one waiter or all waiters.

Control flow: this header does not implement waiting or waking; platform prototype headers declare `__wt_futex_wait` and `__wt_futex_wake`, and platform source files implement them. Higher-level synchronization code stores state in a `WT_FUTEX_WORD`, waits while the word has an expected value, and wakes waiters after changing the word.

State and persistence behavior: futex words are in-memory synchronization state only. They do not persist to disk, but they gate access to shared engine state and can affect the timing of checkpoint, eviction, and shutdown activity.

Dependencies and integration points: it depends only on fixed-width integer definitions and is consumed by Linux, Darwin, Windows, and any common synchronization abstraction that needs `WT_FUTEX_WORD` or `WT_FUTEX_WAKE`.

Risks: the hard 32-bit word contract must remain consistent across all platform implementations. Extending the enum or changing word size would break native futex assumptions and possibly ABI/layout assumptions in synchronization structs. The "not suitable for general use" warning matters because direct use can bypass required memory-ordering and loop/recheck patterns.

Test signals: compile tests across platforms, futex wait/wake behavior tests, and higher-level semaphore/condition stress tests validate this contract.
