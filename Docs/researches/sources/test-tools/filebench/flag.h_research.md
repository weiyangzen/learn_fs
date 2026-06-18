## sources/test-tools/filebench/flag.h

### Purpose
`flag.h` provides a tiny volatile integer flag abstraction used by Filebench code that needs a simple set/clear/query/wait primitive.

### Important APIs, Types, And Functions
It defines `flag_t` as `volatile int` and four static inline functions: `clear_flag`, `set_flag`, `query_flag`, and `wait_flag`. `wait_flag` spins until `query_flag` returns nonzero.

### Control Flow
`clear_flag` writes zero, `set_flag` writes one, `query_flag` tests nonzero, and `wait_flag` is a busy-wait loop. There is no sleeping, yielding, timeout, or memory-barrier operation.

### State And Persistence
The state is entirely the caller-provided integer. The header does not allocate memory or persist anything. Since the integer is volatile, compilers should reload it in the spin loop, but this is not a full synchronization primitive.

### Dependencies And Integration Points
It is included by `filebench.h`, making it widely available throughout the runtime. It can be used for simple inter-thread or signal-adjacent flags where stronger pthread synchronization is not required.

### Risks
`volatile` does not provide atomicity or ordering across threads on all architectures. `wait_flag` can burn CPU indefinitely and has no cancellation path. Concurrent writers/readers can race if callers assume mutex-like behavior.

### Test Signals
Tests should be minimal: compile the inline API, verify set/clear/query behavior, and avoid using `wait_flag` in unit tests without a bounded helper thread. Higher-level tests should prefer pthread condition variables for real synchronization.
