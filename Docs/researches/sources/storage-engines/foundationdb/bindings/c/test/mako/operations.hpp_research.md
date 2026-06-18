# sources/storage-engines/foundationdb/bindings/c/test/mako/operations.hpp

## Purpose
`operations.hpp` declares the data model and iterator helpers for Mako's operation dispatch table. It lets the benchmark express a transaction as a sequence of counted operations, each with one or more steps.

## Important APIs, Types, and Functions
- `StepKind` classifies steps as `NONE`, `IMM`, `READ`, `COMMIT`, or `ON_ERROR`.
- `isAbstractOp` identifies stats-only `OP_COMMIT` and `OP_TRANSACTION`.
- `StepFunction` and `PostStepFunction` define operation callback signatures.
- `Step` stores a kind and function pointers.
- `Operation` exposes `name`, `stepKind`, `stepFunction`, `postStepFunction`, `steps`, and `needsCommit`.
- `OpIterator`, `OpEnd`, `getOpBegin`, and `getOpNext` traverse `Arguments::txnspec`.

## Control Flow
`getOpBegin` skips abstract operations and zero-count operations, returning the first concrete step. `getOpNext` first advances within a multi-step operation, then advances the operation count, then scans for the next enabled operation. Consumers stop at `OpEnd`.

## State and Persistence Behavior
The header stores no mutable state. Iteration state is an `OpIterator` value copied through transaction execution. It indirectly controls persistent FDB changes by determining whether write steps are run and whether a commit is required.

## Dependencies and Integration Points
It depends on `fdb_api.hpp`, `mako.hpp`, and the force-inline macro. `opTable` is defined in `operations.cpp`; all stats and parser code rely on the same `MAX_OP`/`OpKind` ordering.

## Risks
The table supports only two steps per operation, so future multi-step operations require structure changes. `getOpNext` assumes valid, non-abstract current iterators and uses asserts, so malformed internal state can crash debug builds. Step function pointers can be null only for abstract rows that should never be executed.

## Test Signals
Unit-level tests can validate iterator sequences for mixed counts and multi-step operations without connecting to FDB. Integration tests should ensure transaction specs execute in declared order and stop exactly at the configured operation counts.
