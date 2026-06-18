# sources/storage-engines/rocksdb/utilities/transactions/transaction_db_mutex_impl.cc

## Purpose

`transaction_db_mutex_impl.cc` provides RocksDB's default implementation of the `TransactionDBMutexFactory` abstraction. It adapts standard-library `std::mutex` and `std::condition_variable` to the `TransactionDBMutex` and `TransactionDBCondVar` interfaces used by transaction lock managers. The concrete mutex and condition-variable classes are intentionally private to this translation unit; the public header exposes only the factory.

This file supports transaction key-lock waiting in both point-lock and range-lock paths. When a user does not configure `TransactionDBOptions.custom_mutex_factory`, lock managers allocate these default primitives through `TransactionDBMutexFactoryImpl`.

## Important APIs, Types, and Functions

The internal `TransactionDBMutexImpl` class derives from `TransactionDBMutex` and wraps one `std::mutex` (lines 18-33). It implements:

- `Lock()`, which blocks on `mutex_.lock()` and returns `Status::OK()`.
- `TryLockFor(int64_t timeout_time)`, which performs a non-blocking `try_lock` only when `timeout_time == 0`; otherwise it blocks with `mutex_.lock()` and intentionally ignores the timeout for mutex acquisition.
- `UnLock()`, an inline wrapper around `mutex_.unlock()`.

The internal `TransactionDBCondVarImpl` class derives from `TransactionDBCondVar` and wraps one `std::condition_variable` (lines 35-51). It implements:

- `Wait(shared_ptr<TransactionDBMutex>)`, which waits indefinitely.
- `WaitFor(shared_ptr<TransactionDBMutex>, int64_t timeout_time)`, which waits indefinitely for negative timeouts and uses `std::condition_variable::wait_for` for non-negative microsecond timeouts.
- `Notify()` and `NotifyAll()`, mapped to `notify_one` and `notify_all`.

The exported factory methods are `TransactionDBMutexFactoryImpl::AllocateMutex()` and `AllocateCondVar()` (lines 53-60). They allocate the hidden concrete classes and return them as shared pointers to the public interfaces.

## Control Flow

Lock-manager code receives a factory, asks it for a mutex or condition variable, and then calls only the public virtual methods. With the default factory, `AllocateMutex` constructs `TransactionDBMutexImpl`; `AllocateCondVar` constructs `TransactionDBCondVarImpl`.

For mutex acquisition, `Lock()` always blocks until the `std::mutex` is acquired. `TryLockFor(0)` attempts a non-blocking acquisition and returns `Status::TimedOut(Status::SubCode::kMutexTimeout)` when `try_lock` fails. `TryLockFor(timeout != 0)` blocks until the mutex is acquired and returns OK. The comment explains this is deliberate: older GCC versions had known `std::timed_mutex` bugs, and RocksDB expects these mutexes to be held briefly with at most one mutex held at a time. Timeouts are instead enforced on condition-variable waits.

For condition-variable waits, callers pass a `TransactionDBMutex` that is already locked. The implementation downcasts it to `TransactionDBMutexImpl`, constructs a `std::unique_lock<std::mutex>` with `std::adopt_lock`, and calls `wait` or `wait_for`. After the wait returns, it calls `release()` on the `unique_lock` so the lock remains owned by the caller and the destructor does not unlock it. This preserves the interface contract that `Wait` is called with the mutex locked and returns with the mutex still locked.

`WaitFor` treats `timeout_time < 0` as infinite wait. For non-negative values it converts the timeout from microseconds to `std::chrono::microseconds`, uses `wait_for`, and returns `Status::TimedOut(kMutexTimeout)` only when the condition-variable wait reports timeout. Spurious wakeups return OK, matching the public interface.

## State and Persistence Behavior

The file manages only transient synchronization state. No RocksDB data, transaction metadata, or lock table contents are persisted here. The lifetime of each primitive is controlled by `std::shared_ptr` returned from the factory; lock-manager data structures hold those shared pointers.

`TransactionDBMutexImpl` stores one `std::mutex`, and `TransactionDBCondVarImpl` stores one `std::condition_variable`. The condition variable does not own the mutex; it relies on callers passing a compatible default mutex implementation. The downcast makes that compatibility assumption explicit.

Timeout state is not persisted. The only status-bearing behavior is returning `TimedOut(kMutexTimeout)` from non-blocking mutex acquisition failure or condition-variable timeout.

## Dependencies and Integration Points

This file depends on:

- `utilities/transactions/transaction_db_mutex_impl.h` for the factory declaration.
- `rocksdb/utilities/transaction_db_mutex.h` for the abstract mutex, condition variable, and factory interfaces.
- Standard `<mutex>`, `<condition_variable>`, and `<chrono>` for implementation.
- RocksDB `Status` and `Status::SubCode::kMutexTimeout` through the public mutex header.

Integration points include point lock manager stripes, range tree lock manager portability wrappers, and any transaction DB code that uses `TransactionDBOptions.custom_mutex_factory`. Adjacent references show point lock manager code defaults to `std::make_shared<TransactionDBMutexFactoryImpl>()` when no custom factory is configured, and range lock code also instantiates this implementation for default behavior.

## Risks and Edge Cases

The main risk is the `static_cast<TransactionDBMutexImpl*>` in condition-variable waits. It is correct only when the mutex was allocated by this same default factory. If a custom factory mixes a custom mutex with this condition variable, behavior is undefined. The intended contract is that a factory produces compatible mutex and condition-variable implementations as a pair.

Timeout semantics are deliberately uneven. `TryLockFor(timeout > 0)` can block longer than the requested timeout because it ignores the timeout while acquiring the mutex. Lock acquisition timeout is only honored for `timeout == 0`; positive timeouts are effectively deferred to `WaitFor`. This is documented in-code, but it is a behavioral detail that tests and custom implementations should not accidentally assume away.

The use of `std::adopt_lock` requires the passed mutex to already be locked by the current thread. Passing an unlocked mutex or a mutex locked by another thread violates the standard-library precondition and can lead to undefined behavior. That is why this implementation must remain tightly coupled to the lock-manager calling convention.

Condition variables can wake spuriously, and the implementation returns OK in that case. Callers must always re-check their lock-table predicates after waiting.

The file includes `<sstream>` and `<thread>` even though this implementation does not use them; this is harmless but may be leftover include noise.

## Test Signals

Useful tests should exercise successful lock/unlock, non-blocking `TryLockFor(0)` timeout behavior, `WaitFor` timeout behavior in microseconds, negative-timeout infinite waits, `Notify` waking one waiter, `NotifyAll` waking all waiters, and spurious-wakeup-safe lock-manager loops. Integration tests in point and range transaction locking are more valuable than unit tests against these wrappers alone because the correctness depends on caller-side predicate checks and lock ownership conventions.

Concurrency tests should also verify that lock-manager operations do not rely on positive `TryLockFor` enforcing a strict mutex acquisition deadline. The deadline that matters for real contention is the condition-variable wait path.
