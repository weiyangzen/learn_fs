# sources/storage-engines/foundationdb/bindings/c/test/apitester/TesterScheduler.h

## Purpose
`TesterScheduler.h` declares the asynchronous scheduler abstraction used by the C API tester framework.

## Important APIs, Types, And Functions
- `TTaskFct` is `std::function<void(void)>`.
- `NO_OP_TASK` is declared as a reusable empty continuation.
- `ITimer` declares `cancel()`.
- `IScheduler` declares lifecycle methods `start`, `schedule`, `scheduleWithDelay`, `stop`, and `join`.
- `createScheduler(int numThreads)` constructs an implementation.

## Control Flow
The header defines the interface; implementations post tasks and timers asynchronously. Workloads use `TTaskFct` continuations throughout the framework.

## State And Persistence Behavior
No state is held in the header. Implementations manage scheduler threads/timers. There is no persistent database behavior.

## Dependencies And Integration Points
It depends on `<functional>` and `<memory>`. It is implemented by `TesterScheduler.cpp` and used by workload manager/executor code to decouple tests from a specific async backend.

## Risks And Edge Cases
Callers must respect scheduler lifecycle: tasks should not be posted after shutdown, and timers must be canceled or allowed to fire before destruction depending on desired behavior. A task that never schedules its continuation can stall a workload.

## Test Signals
Indirect runtime coverage comes from every API tester workload. Compile coverage validates the abstraction boundary.
