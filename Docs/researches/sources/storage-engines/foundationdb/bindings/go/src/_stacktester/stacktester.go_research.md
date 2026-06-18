# sources/storage-engines/foundationdb/bindings/go/src/_stacktester/stacktester.go

## Purpose

`stacktester.go` is the Go binding executable stack tester. It reads generated instruction tuples from FoundationDB, interprets them against the Go binding API, and uses stack results/logging to validate that Go binding behavior matches other FoundationDB bindings. It covers transactions, read snapshots, range reads, tuple encoding, atomic operations, conflict ranges, watches, locality, API options, and directory operations delegated to `directory.go`.

## Important APIs, Types, and Functions

`StackMachine` holds the instruction prefix, current transaction name, stack, last read/committed version, spawned goroutine wait group, verbosity flag, and `DirectoryExtension`. `stackEntry` preserves the producer instruction index with each value. `waitAndPop` normalizes immediate values and FDB futures, converting ready results into plain Go values and FDB errors into encoded `ERROR` tuples.

Helpers such as `popSelector`, `popKeyRange`, `popRangeOptions`, `pushRange`, `executeMutation`, `currentTransaction`, `newTransaction`, and `switchTransaction` support the instruction interpreter. `processInst` is the large dispatcher for stack, transaction, tuple, range, conflict, atomic, unit-test, and directory operations. `Run` fetches instructions from `tuple.Tuple{prefix}` and executes them in order. `main` selects the API version, opens the database, and runs the machine.

## Control Flow

The executable expects `prefix api_version [cluster_file]`. After API selection and database open, `Run` reads all instruction key-values under the tuple prefix in a transaction and unpacks each value as an instruction tuple. For every instruction, `processInst` chooses the active transactor/read-transactor based on `_SNAPSHOT` and `_DATABASE` suffixes, then executes the opcode.

Database-suffixed mutations use `db.Transact` through `executeMutation` and push `RESULT_NOT_PRESENT`. Transaction-scoped operations use the named transaction in `trMap` and leave commit/on-error behavior explicit. `START_THREAD` spawns another `StackMachine` on a different prefix and waits at the end of `Run`.

## State and Persistence Behavior

Process state includes global `db`, global named transaction map guarded by `trMapLock`, per-machine stack, last version, and directory object list. Persistent effects are all FoundationDB operations performed by instructions: key mutations, range clears, atomic ops, log-stack writes, watch setup side effects, locality system-key reads, and directory metadata/content changes.

The stack stores FDB futures as first-class values, allowing generated tests to delay `Get`/`MustGet` until `WAIT_FUTURE` or a later pop. Errors from FDB futures are encoded as stack values where the protocol expects that, while unexpected non-FDB panics abort the process.

## Dependencies and Integration Points

The file depends on the Go binding packages `fdb` and `tuple`, standard libraries for binary encoding, reflection, synchronization, and runtime scheduling, and directory support in the sibling `directory.go`. It is built by the Go binding CMake file as `fdb_go_tester` and run by generated stack-test harnesses.

## Risks

The dispatcher is intentionally broad and type-assertion heavy; malformed instruction streams can panic or fatal. Atomic operations are invoked by reflection from transformed operation names, so method naming must stay aligned with the binding API. `WAIT_EMPTY` ignores the returned error from `db.Transact`, which may hide retry exhaustion or fatal errors. Range mode maps instruction values by adding one to the `StreamingMode`, a protocol detail that must stay aligned with generated instructions. Futures should not escape transaction lifetimes outside expected tester patterns.

## Test Signals

The executable is validated by stack tester suites. High-value signals include cross-binding result equivalence, successful tuple round trips including versionstamps and floats, watch triggering behavior, locality boundary consistency, API option calls, database retry behavior, named transaction switching, concurrent thread prefixes, and directory instruction compatibility.
