# sources/storage-engines/foundationdb/bindings/flow/tester/Tester.h

## Purpose

`Tester.h` declares the shared data model and dispatcher support for the Flow binding stack tester. It defines stack entries, instruction metadata, directory/subspace tracking, global tester state, and the mutation retry helper used by instruction implementations. The header forms the contract between `Tester.cpp` and other tester modules such as directory instruction implementations.

## Important APIs, Types, and Functions

`StackItem` binds an instruction index to a `Future<Standalone<StringRef>>`, allowing stack values to be either immediate tuple-packed strings or pending asynchronous results. `FlowTesterStack` provides push/pop, tuple-value pushes, error tuple encoding, future-aware `waitAndPop`, duplication, and clear operations.

`InstructionData` carries execution flags (`isDatabase`, `isSnapshot`), the original packed instruction, and the selected Flow transaction. `InstructionFunc` is an `IDispatched` command dispatcher keyed by operation name. `REGISTER_INSTRUCTION_FUNC` wraps the registration macro used by concrete instruction structs.

Directory support is modeled by `DirectoryOrSubspace` and `DirectoryTesterData`. A slot can hold an `IDirectory`, a `Subspace`, both for a `DirectorySubspace`, or an invalid placeholder. `FlowTesterData` aggregates the FDB API pointer, database handle, fetched instruction range, current transaction name, stack, last version, directory state, and futures for spawned subthreads. The templated `executeMutation` helper retries database-scoped mutations on retryable errors and commits when the instruction is marked as database-level.

## Control Flow

Instruction implementations receive `Reference<FlowTesterData>` and `Reference<InstructionData>` through `InstructionFunc::call`. The dispatcher validates that the operation exists and invokes the registered callable. Stack operations can defer waiting until later by pushing futures; callers that need concrete tuple values call `waitAndPop`.

`executeMutation` loops around a caller-supplied async function. On success it commits only for `_DATABASE` instructions; on an FDB `Error`, it calls `tr->onError` for database-scoped operations and rethrows for transaction-scoped operations so explicit transaction tests can observe failures.

## State and Persistence Behavior

The header declares in-memory structures only. Persistence occurs when instruction implementations use the database or directory layer. `FlowTesterStack` preserves instruction indexes with values so logged output can map stack results back to the instruction that produced them. `DirectoryTesterData` starts with a root `DirectoryLayer` and appends results or invalid placeholders as directory instructions execute.

## Dependencies and Integration Points

The header depends on Flow reference/future infrastructure, the Flow FDB binding, tuple/subspace/directory abstractions, and `IDispatched`. It is consumed by the Flow tester executable and any companion source that registers additional instructions. Its dispatcher keys and data shapes must remain compatible with generated stack tester instruction streams.

## Risks

`FlowTesterStack::pop` returns fewer than requested items when the stack is short, leaving each instruction to decide whether to no-op. `DirectoryTesterData::directory` and `subspace` assert on invalid access rather than returning errors. `DirectoryOrSubspace` stores a raw `Subspace*` when constructed from a raw subspace, so lifetime must be owned elsewhere; directory subspaces are safe only while the referenced object remains alive. `executeMutation` retries forever until `onError` reports a non-retryable failure.

## Test Signals

Useful signals are successful compilation of all registered instruction modules and stack tester runs that exercise immediate values, futures, database-suffixed auto-commit operations, explicit transaction operations, and directory object indexing. Assertion failures in directory/subspace access usually indicate an instruction ordering or error-placeholder mismatch.
