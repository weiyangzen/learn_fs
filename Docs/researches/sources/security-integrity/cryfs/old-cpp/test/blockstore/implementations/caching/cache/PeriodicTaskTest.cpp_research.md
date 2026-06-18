# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/PeriodicTaskTest.cpp

Purpose: tests lifecycle and callback behavior for `PeriodicTask`.

Important APIs/types/functions: `AtomicCounter`, `PeriodicTaskTest`, `PeriodicTask`, `waitForZero`, and callback lambdas.

Control flow: constructs a task and destroys it immediately, waits for at least ten rapid callbacks using a condition variable, and verifies no callback runs after task destruction.

State and persistence behavior: in-memory background task state only; atomic/counter objects track callback execution.

Dependencies and integration points: uses `PeriodicTask`, mutex/condition variable, atomics, GoogleTest, and Boost thread sleep.

Risks and test signals: covers destructor deadlock and post-destruction callback safety. Timing-based tests with 1 ms periods can be sensitive to scheduler delays.
