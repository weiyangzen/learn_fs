## sources/storage-engines/foundationdb/fdbserver/workloads/RandomMoveKeys.cpp

`MoveKeysWorkload` (`NAME = "RandomMoveKeys"`) is a simulation failure injection workload that disables DD and repeatedly issues random `moveKeys` operations over random key ranges to random storage teams. It stresses relocation, cancellation of overlapping relocations, and data distribution recovery after manual damage.

Important APIs and types include `FailureInjectionWorkload`, `DatabaseConfiguration`, `configKeys`, `setDDMode`, `takeMoveKeysLock`, `getStorageServers`, `MoveKeysParams`, `moveKeys`, `KeyRangeMap`, `KeyRangeActorMap`, `newDataMoveId`, `DataMoveType`, `DataMovementReason`, and locality fields on `StorageServerInterface`.

`start` reads configuration from system keys to learn storage team size, disables DD, runs `worker` for `testDuration`, and restores the old DD mode. `worker` takes the move-keys lock, filters duplicate-address and TSS storage servers, then loops at a poisson rate. For each random range it selects a random team with unique zones/data halls, cancels in-flight actors affected by the inserted range, updates an in-flight range map, and starts `doMoveKeys` for every affected range. `doMoveKeys` builds logical or physical data movement parameters depending on `SHARD_ENCODE_LOCATION_METADATA` and the physical move probability knob.

State and persistence include data-move metadata, shard location changes, and DD mode. The workload intentionally perturbs real shard placement and relies on restoring DD and a delayed `check` to let the database heal. Risks include no support for multi-region usable regions, operation failures when too few unique machines exist, broad overlap cancellation, and DD mode restoration being skipped if an unexpected error escapes before the final set mode.

Integration points are DD locking, storage team selection, physical/logical shard movement, failure injection selection, and simulator-only operation. Test signals are relocation trace intervals and downstream workload/database health after the delayed `check`, which returns true after `testDuration / 2`.
