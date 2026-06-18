# sources/storage-engines/tikv/components/raftstore/src/coprocessor/read_write/mod.rs

## Purpose
This module is the namespace for read/write observation support added under raftstore coprocessors.

## Important APIs, Types, And Functions
It declares `snapshot` and `write_batch` submodules and re-exports their public contents: `ObservedSnapshot`, `SnapshotObserver`, `ObservableWriteBatch`, `WriteBatchObserver`, and `WriteBatchWrapper`.

## Control Flow
There is no runtime logic here. Consumers import through `coprocessor::read_write` or through `coprocessor/mod.rs` re-exports.

## State And Persistence Behavior
No state or persistence is implemented in this file. The submodules define the actual snapshot/write-batch observation behavior.

## Dependencies And Integration Points
The module is used by `dispatcher.rs` for boxed observer registration and by `coprocessor/mod.rs` for public re-exports.

## Risks
Because this is a thin module, the main risk is API visibility drift: adding a new read/write observer type requires updating re-exports if external callers should use it.

## Test Signals
No direct tests; coverage is through `write_batch.rs`, `snapshot.rs`, and dispatcher integration.
