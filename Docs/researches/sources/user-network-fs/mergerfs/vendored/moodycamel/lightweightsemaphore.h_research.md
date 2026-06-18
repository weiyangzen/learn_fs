# sources/user-network-fs/mergerfs/vendored/moodycamel/lightweightsemaphore.h

## Purpose

This header vendors `moodycamel::LightweightSemaphore`, a small C++11 semaphore abstraction used by moodycamel blocking queues and other producer/consumer code. It combines an atomic count with a platform semaphore so uncontended waits remain cheap while contended waits sleep in the operating system.

## Important APIs, Types, And Functions

- `moodycamel::details::Semaphore` is a platform wrapper. Implementations exist for Windows, Mach/Darwin, POSIX Unix, and z/OS. It exposes `wait`, `try_wait`, `timed_wait`, and `signal`.
- `moodycamel::LightweightSemaphore` is the public type. It defines signed `ssize_t`, stores `std::atomic<ssize_t> m_count`, a `details::Semaphore m_sema`, and `int m_maxSpins`.
- Public methods are `tryWait`, `wait()`, `wait(timeout_usecs)`, `tryWaitMany(max)`, `waitMany(max, timeout_usecs)`, `waitMany(max)`, `signal(count)`, and `availableApprox()`.
- Private helpers `waitWithPartialSpinning` and `waitManyWithPartialSpinning` implement the spin-then-block paths and timeout repair logic.

## Control Flow

Construction asserts non-negative initial count and spin count, initializes the atomic count, and initializes the underlying platform semaphore with its default initial count. Fast-path `tryWait` repeatedly loads `m_count` and uses CAS to decrement it only when it is positive. `wait()` first calls `tryWait`; if no token is available it enters `waitWithPartialSpinning`.

`waitWithPartialSpinning` spins up to `m_maxSpins`, each time trying to decrement a positive count with acquire semantics and using `atomic_signal_fence` to keep the compiler from collapsing the loop. If spinning fails, it decrements `m_count`. A positive old count means it acquired a token without sleeping. A non-positive old count means it is now represented as a waiter, so it blocks on the OS semaphore for indefinite waits or uses the platform timed wait for positive timeouts.

If a timed wait expires, the method must repair `m_count` because it already decremented it before sleeping. The repair loop either consumes a semaphore signal that arrived after timeout bookkeeping (`oldCount >= 0 && m_sema.try_wait()`) or CAS-increments a negative waiter count back toward zero and returns false.

`tryWaitMany` greedily decrements up to `max` available tokens with one CAS. `waitManyWithPartialSpinning` first tries the same spin/CAS approach, otherwise blocks for one token and then greedily drains additional tokens with `tryWaitMany(max - 1)`. `signal(count)` release-adds to `m_count` and signals the OS semaphore only for the portion of `count` that corresponds to negative pre-existing waiters.

## State And Persistence Behavior

The semaphore has no persistent state outside process memory. `m_count` is positive for available tokens, zero for no available tokens/no known waiters, and negative when waiters have decremented the count before blocking. The platform semaphore is the sleep/wakeup mechanism for negative-count waiters. `availableApprox()` is a relaxed snapshot and returns zero for non-positive counts.

Platform wrappers own OS resources: Windows closes the handle, Mach destroys the Mach semaphore, and POSIX/zOS calls `sem_destroy`. Copy construction and assignment are disabled.

## Dependencies

The header depends on C++ atomics, assertions, errno handling, `std::size_t`, integer types, `clock_gettime`, and `std::make_signed`. Platform dependencies are direct declarations of Windows semaphore APIs, Mach semaphore APIs, z/OS semaphore APIs, or POSIX `sem_t`. On glibc 2.30+ with `_GNU_SOURCE`, POSIX timed waits use `sem_clockwait` with `CLOCK_MONOTONIC`; otherwise they use `sem_timedwait` with `CLOCK_REALTIME`.

## Integration Points

This file is the low-level wait primitive for moodycamel blocking queues. The default spin count matches `ConcurrentQueueDefaultTraits::MAX_SEMA_SPINS`, and blocking queue code can tune spin behavior through construction. It is header-only and does not include `windows.h`, which keeps global namespace pollution low for mergerfs translation units.

## Risks And Edge Cases

- Unsupported platforms fail at compile time with `#error Unsupported platform!`.
- Timed waits use microseconds, but Windows converts to milliseconds by integer division, so sub-millisecond waits become zero-millisecond waits.
- POSIX non-monotonic timed waits use `CLOCK_REALTIME`; system clock adjustments can affect timeout duration unless the monotonic glibc path is enabled.
- `signal(count)` casts the number of OS releases to `int`; extremely large counts beyond `int` range would be unsafe even though normal use signals modest counts.
- `waitMany(max)` asserts that it acquired at least one token. Passing zero to the no-timeout overload is inconsistent with that assertion and should be avoided.
- Like most synchronization primitives, destruction while threads may be waiting is unsafe and must be externally synchronized.
- The repair loop after timeout is subtle. Changes to memory ordering or semaphore try-wait behavior can introduce lost wakeups.

## Test Signals

Validation should cover uncontended `tryWait`/`signal`, many waiters woken by one `signal(count)`, timeout expiration, signals racing with timeout repair, `waitMany` greedy acquisition, and destruction only after all waiters have joined. Platform CI should compile at least Linux/POSIX and any target OS mergerfs supports. On Linux, tests should exercise both realtime and monotonic timed wait builds when feature macros permit.
