# sources/storage-engines/wiredtiger/tools/memory-model-test/basic_semaphore.h

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/memory-model-test/basic_semaphore.h -->
## sources/storage-engines/wiredtiger/tools/memory-model-test/basic_semaphore.h

### Purpose
`basic_semaphore.h` implements a minimal counting semaphore used as a fallback for compilers lacking C++20 `std::binary_semaphore`.

### Important APIs, Types, and Functions
`basic_semaphore` has a constructor with initial count, `acquire()` that waits on a condition variable while count is zero and decrements it, and `release()` that increments count and notifies one waiter. Private state is `_mutex`, `_condition_variable`, and `_count`.

### Control Flow
`acquire` locks, waits in a loop to handle spurious wakeups, and consumes one count. `release` locks, increments, and signals.

### State and Persistence
State is purely in-memory synchronization state. It is process-local and not persistent.

### Dependencies and Integration Points
It depends on `<mutex>` and `<condition_variable>`. `memory_model_test.cpp` aliases it to `binary_semaphore` when `AVOID_CPP20_SEMAPHORE` is defined.

### Risks and Test Signals
It is a counting semaphore despite being used as a binary semaphore; repeated releases can accumulate permits. It does not enforce nonnegative construction. Concurrency tests should cover acquire blocking, release waking one waiter, spurious wake tolerance, and repeated release behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/tools/memory-model-test/basic_semaphore.h -->
