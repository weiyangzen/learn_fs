# sources/storage-engines/foundationdb/bindings/flow/tester/Tester.cpp

## Purpose

`Tester.cpp` implements the executable Flow binding stack tester for FoundationDB. It reads test instructions from the database under a tuple-prefixed range, interprets them as stack-machine operations, executes Flow binding APIs, and writes/logs results back through the shared stack abstraction. Its role is cross-binding compatibility testing: the instruction vocabulary mirrors operations implemented by the Go stack tester and other language testers so that the same generated instruction stream can validate tuple encoding, transactions, range reads, atomic operations, conflicts, threading, and directory-layer integration behavior.

## Important APIs, Types, and Functions

The file registers many `InstructionFunc` implementations through `REGISTER_INSTRUCTION_FUNC`, using the dispatcher declared in `Tester.h`. Core stack instructions include `PUSH`, `DUP`, `EMPTY_STACK`, `SWAP`, `POP`, `SUB`, `CONCAT`, and `LOG_STACK`. Transaction and database instructions include `NEW_TRANSACTION`, `USE_TRANSACTION`, `ON_ERROR`, `SET`, `GET`, `COMMIT`, `RESET`, `CANCEL`, `GET_KEY`, range variants, conflict range/key operations, `ATOMIC_OP`, and API/option validation in `UNIT_TESTS`. Tuple instructions include pack/unpack/range/sort plus float and double encode/decode helpers.

`getRange` has two overloads: one for `KeyRange` and one for selector ranges. Both manually continue paged range reads until `more` is false or an explicit limit is reached, including an iterator streaming-mode progression copied from the C API. `waitForVoid`, `waitForValue`, and `getKey` normalize asynchronous results and errors into tuple-packed stack values. `startTest`, `runTest`, `getInstructions`, and `doInstructions` are the top-level execution pipeline, while `main` parses `prefix`, `api_version`, and optional cluster filename.

## Control Flow

`main` initializes platform/crash handling, selects deterministic randomness, starts `startTest`, and then runs the Flow network until stopped. `startTest` initializes global atomic-op and directory-creating-op maps, creates the Flow network, selects the requested API version, starts the network thread, opens the database, and invokes `runTest`. `runTest` fetches instruction key-values under the supplied tuple prefix, executes them in order, then waits for subthreads spawned by `START_THREAD`.

For each instruction, `doInstructions` unpacks the operation tuple, strips `_DATABASE` or `_SNAPSHOT` suffixes, chooses either a new auto-committed transaction or the named transaction from `trMap`, rejects snapshot directory operations, and dispatches by operation string. Database-suffixed mutations use `executeMutation`, which wraps the mutation in a retry loop and commits automatically. Transaction-scoped mutations run against the current transaction and leave commit timing to explicit instructions.

## State and Persistence Behavior

Persistent state lives primarily in FoundationDB: instruction streams are read from the database, mutations apply to keys passed by the generated test, and `LOG_STACK` writes stack entries to a caller-provided prefix in batches of 100. In-process state includes global `trMap`, the current transaction name, `lastVersion`, stack entries containing futures, and `DirectoryTesterData`. `START_THREAD` creates a separate `FlowTesterData` with the same database handle and independent stack/directory state, then records the future in `subThreads`.

The stack deliberately stores futures as values so instructions can test asynchronous ordering and explicit `WAIT_FUTURE`. Error results are encoded as tuple values rather than always aborting the whole tester, except for assertions and unexpected top-level errors. Directory instruction failures receive special handling: if the operation is known to create or open a directory-like object, an invalid placeholder is appended to preserve directory-list index alignment, and `DIRECTORY_ERROR` is pushed.

## Dependencies and Integration Points

The implementation depends on Flow coroutine `Future`/`Reference` APIs, `bindings/flow/fdb_flow.h`, tuple and directory binding types, `fdbrpc` network setup, deterministic random, and TLS configuration. It is built into the FoundationDB binding test infrastructure and expects a running FDB cluster or cluster file. It integrates with the Flow directory tester through shared `DirectoryTesterData` and directory instruction names, although the directory instruction bodies are defined elsewhere.

The instruction vocabulary is an integration contract with generated stack-tester workloads and other language binding testers. Atomic operation names are mapped to `FDBMutationType`, and `UNIT_TESTS` verifies API version selection and option-setting wrappers against the Flow binding surface.

## Risks

Global `trMap` and `optionInfo` are mutable process-wide state; subthreads share the transaction map without visible synchronization in this file. Several helpers use raw casts for floats, doubles, UUID formatting, and integer byte order, so strict-aliasing or alignment assumptions matter. Some stack operations silently no-op on underflow, which matches tester behavior but can hide malformed instruction streams. `getRange` carries a copied C API iterator progression with a comment noting maintenance risk if the C implementation changes. Directory error handling depends on the hard-coded `opsThatCreateDirectories` set staying aligned with registered directory operations.

## Test Signals

This file is itself a test executable. Strong signals are successful execution of generated binding stack tests across API versions, matching result logs against other language bindings, and coverage of `UNIT_TESTS`, watch/locality-equivalent operations, tuple round trips, range selector variants, and database-suffixed retry behavior. Build/test signals come from the Flow binding tester target and any suite that invokes `fdb_flow_tester prefix api_version [cluster_filename]`.
