## sources/storage-engines/foundationdb/bindings/flow/fdb_flow.h

Purpose: public Flow binding API declarations over the FoundationDB C API.

Important APIs and types: `CFuture` owns `FDBFuture*`; `FDBStandalone<T>` extends result types with a future reference; abstract `ReadTransaction`, `Transaction`, `Database`, and `API` define async operations, mutation operations, admin calls, network lifecycle, database creation, and error predicate evaluation.

Control flow: users select an API version, configure/run the network, create a database, create transactions, perform async operations returning Flow `Future`s, and commit or retry via `onError`.

State and persistence: abstract interfaces represent database and transaction handles. `FDBStandalone` is the important ownership state carrier for borrowed C future memory.

Dependencies and integration points: includes Flow primitives, latest bindings C API, and `FDBLoanerTypes`. Implemented by `fdb_flow.cpp` and consumed by directory, tuple, subspace, allocator, and tester code.

Risks: all operations assume correct network lifecycle. Borrowed result memory must be retained through `FDBStandalone`; dropping it too early invalidates refs. API version selection is singleton-based.

Test signals: compilation and execution of `fdb_flow_tester` and C API tests validate this interface.
