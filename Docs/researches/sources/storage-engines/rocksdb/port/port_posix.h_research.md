# sources/storage-engines/rocksdb/port/port_posix.h

Purpose: POSIX port declarations for RocksDB's platform abstraction. It normalizes endian detection, cache-line sizing, synchronization primitives, thread aliases, direct CPU pause instructions, process helpers, page allocation, and crash/exit behavior for non-Windows builds.

Important APIs/types/functions: `port::Mutex`, `RWMutex`, and `CondVar` wrap `pthread_mutex_t`, `pthread_rwlock_t`, and `pthread_cond_t`; `Thread` aliases `std::thread`; `OnceType`/`InitOnce` wrap `pthread_once_t`; `AsmVolatilePause`, `PhysicalCoreID`, `cacheline_aligned_alloc/free`, `Crash`, `ImmediateExit`, `GetMaxOpenFiles`, `SetCpuPriority`, `GetProcessID`, and `GenerateRfcUuid` are the public port hooks.

Control flow: this header is mostly compile-time dispatch. It chooses platform endian headers, substitutes missing unlocked stdio/fdatasync APIs, defines `PREFETCH`, and exposes declarations implemented in POSIX source files.

State and persistence behavior: only synchronization objects own state. Persistence-related behavior is indirect through `ImmediateExit`, which avoids static destruction when background threads may still touch global objects.

Dependencies and integration points: consumed by `port/port.h`, env/file-system code, mutex users, cache-aligned structures, and low-level utilities. It depends on pthreads, endian headers, process IDs, and RocksDB namespace/port definitions.

Risks and test signals: endian/cache-line macros are build-sensitive; debug `Mutex::AssertHeld` does not prove current-thread ownership; platform fallback definitions need coverage on BSD, AIX, Solaris, Android, and Linux. Tests that exercise port primitives, cache alignment, process ID, UUID generation, and immediate-exit paths signal regressions.
