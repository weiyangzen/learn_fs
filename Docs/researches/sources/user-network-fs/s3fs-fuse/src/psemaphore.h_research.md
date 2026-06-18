# sources/user-network-fs/s3fs-fuse/src/psemaphore.h

## Purpose
Defines a portable `Semaphore` abstraction for s3fs-fuse. It uses C++20 `std::counting_semaphore` when available, Grand Central Dispatch semaphores on macOS for pre-C++20 builds, and POSIX `sem_t` elsewhere.

## Important APIs, Types, And Functions
For C++20 and newer, `using Semaphore = std::counting_semaphore<INT_MAX>`. On macOS, the class wraps `dispatch_semaphore_t` with constructor, destructor, deleted copy/move, `acquire()`, `try_acquire()`, and `release()`. On non-Apple pre-C++20 platforms, the class wraps `sem_t` with `sem_init()`, `sem_destroy()`, `sem_wait()` retrying on `EINTR`, `sem_trywait()` retrying on `EINTR`, and `sem_post()`.

## Control Flow
Preprocessor selection is the main control flow. The POSIX `acquire()` loop blocks until `sem_wait()` succeeds or fails for an error other than `EINTR`, but it does not surface non-EINTR failures. `try_acquire()` retries on interrupt and returns true only on immediate acquisition. The macOS destructor posts `value` times before `dispatch_release()` because the comment states macOS cannot destroy a semaphore with fewer posts than its initializer.

## State And Persistence Behavior
Semaphore state is in process memory and owned by the underlying standard library, dispatch object, or POSIX semaphore. The wrapper is non-copyable and non-movable in custom implementations. There is no file or interprocess persistence; POSIX `sem_init()` uses `pshared = 0`.

## Dependencies And Integration Points
The C++20 path depends on `<semaphore>` and `INT_MAX`; the Apple path depends on `<dispatch/dispatch.h>`; the POSIX path depends on `<cerrno>` and `<semaphore.h>`. This header can be included by request/thread coordination code that needs a uniform counting semaphore across Linux, macOS, and newer C++ builds.

## Risks
The C++20 branch uses `INT_MAX` without including `<climits>` in this header, relying on prior includes or implementation leakage. The POSIX constructor and destructor ignore `sem_init()`/`sem_destroy()` return values, and `acquire()` ignores non-EINTR failures. The macOS destructor's forced releases can wake waiting threads during object destruction if lifetime is not externally quiesced. The C++20 alias lacks deleted copy/move declarations from the custom classes, so exact type traits differ by standard version.

## Test Signals
Build tests should cover C++20, macOS pre-C++20, and POSIX pre-C++20 configurations. Runtime tests should verify acquire/release counting, failed `try_acquire()` on zero count, retry after signal interruption on POSIX, and safe destruction only after users stop waiting. Static checks should confirm `<climits>` availability or add it if the C++20 path fails in isolation.
