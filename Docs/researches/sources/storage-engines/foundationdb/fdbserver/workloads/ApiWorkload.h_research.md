# sources/storage-engines/foundationdb/fdbserver/workloads/ApiWorkload.h

## Purpose
`ApiWorkload.h` declares the transaction abstraction and base workload used by FoundationDB API correctness tests. It lets one workload run against native Flow transactions, ReadYourWrites transactions, thread-safe transactions, and multi-version transactions while keeping a common in-memory oracle.

## Important APIs, Types, and Functions
- `TransactionType`: `NATIVE`, `READ_YOUR_WRITES`, `THREAD_SAFE`, `MULTI_VERSION`.
- `TransactionWrapper`: abstract interface for set, commit, get, range reads, mapped range reads, key selectors, clear, `onError`, version queries, span context, debug, and conflict ranges.
- `FlowTransactionWrapper<T>`: adapts Flow transaction types and can recreate transactions against an extra simulated DB after errors.
- `ThreadTransactionWrapper`: adapts thread-safe `ITransaction` by converting thread futures into Flow futures.
- `TransactionFactoryInterface` and `TransactionFactory<T, DB>`: construct transaction wrappers.
- `ApiWorkload : TestWorkload`: owns options, prefix, success state, data-generation settings, memory store, and selected transaction factory.

## Control Flow
The constructor reads workload options, computes a formatted per-client prefix, initializes random key/value bounds, and discovers any simulator extra database. Subclasses use implementation methods from `ApiWorkload.cpp`: setup clears the prefix and delegates `performSetup`; start generates data and delegates `performTest`. After `chooseTransactionFactory`, subclass logic calls `createTransaction` and operates through `TransactionWrapper`.

## State and Persistence Behavior
The header defines runtime state rather than persistence logic. `ApiWorkload` keeps the per-client prefix and `MemoryKeyValueStore` oracle. Database persistence happens only through wrapper transactions used by subclasses. `transactionFactory` is reference-counted state for the chosen API; `transactionType` records the selected mode. `extraDB` is simulation-only.

## Dependencies and Integration Points
The header depends on tester workload infrastructure, `ClusterConnectionMemoryRecord`, `ReadYourWrites`, `ThreadSafeTransaction`, and `MemoryKeyValueStore`. It is included by API workload implementations and forms a compatibility layer over NativeAPI, RYW, ThreadSafe, and MultiVersion transaction stacks.

## Risks
The wrapper interface must evolve with transaction API changes; every new required semantic needs both Flow and thread-safe implementations. `ThreadTransactionWrapper` ignores extra DB routing. `FlowTransactionWrapper::lastTransaction` preserves old transaction lifetime after `onError`, which can matter if futures survive. Some exposed methods, such as mapped ranges or span context, may have low coverage unless workloads explicitly exercise them.

## Test Signals
There are no direct tests in the header. It is exercised by `ApiCorrectness` through random transaction-type selection. Compile coverage is meaningful because all wrappers must satisfy the virtual interface.
