# sources/storage-engines/foundationdb/fdbserver/backupworker/include/fdbserver/backupworker/BackupWorkerRangePartitioned.h

## Purpose
This header publishes the range-partitioned backup worker actor to fdbserver components.

## Important APIs and Types
It forward-declares `InitializeRangeBackupRequest` and `ServerDBInfo`, includes `BackupInterface` and Flow primitives, and declares:

`Future<Void> backupWorkerRangePartitioned(BackupInterface bi, InitializeRangeBackupRequest req, Reference<AsyncVar<ServerDBInfo> const> db);`

The request type differs from the classic worker so callers can pass range-backup-specific recruitment state, including backup tag, epochs, start/end versions, and total tag count.

## Control Flow and Integration
The actor is intended to be started by backup worker recruitment code for range-partitioned backup mode. It owns its lifetime and reports completion to the cluster interface when an epoch is done. The implementation currently includes a force-link test shim, suggesting production call sites may still be in progress.

## State, Risks, and Test Signals
The header stores no state. Signature drift can break recruitment sites. Since this actor depends on partition-map setup before pulling mutations, callers must provide a request compatible with the tlog partition-map stream. Unit/link tests in the backupworker target help ensure implementation availability.
