# sources/storage-engines/rocksdb/monitoring/instrumented_mutex.h

Purpose: Declares instrumented wrappers around RocksDB port mutexes and condition variables, plus RAII lock/unlock helpers.

Important APIs/types/functions: `InstrumentedMutex` wraps `Lock`, `Unlock`, and `AssertHeld` while retaining optional statistics/clock/ticker metadata. `CacheAlignedInstrumentedMutex` enforces cache-line alignment. `InstrumentedMutexLock` locks/unlocks by RAII. `InstrumentedMutexUnlock` temporarily releases and reacquires. `InstrumentedCondVar` exposes `Wait`, `TimedWait`, `Signal`, and `SignalAll`.

Control flow/integration: DB internals can use these wrappers in place of `port::Mutex` to get monitoring data through `StatisticsImpl` and perf context without changing lock call sites much.

State and dependencies: State is the underlying mutex/condvar plus monitoring pointers and stats code. The condition variable shares the mutex's monitoring metadata. Depends on `monitoring/statistics_impl.h`, `rocksdb/system_clock.h`, `rocksdb/thread_status.h`, and `util/stop_watch.h`.

Risks/test signals: Statistics pointers are non-owning and must outlive the instrumented object. RAII helpers are non-copyable. The cache-aligned class has a static assertion guarding alignment-size consistency.
