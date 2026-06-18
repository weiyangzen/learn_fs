# sources/storage-engines/foundationdb/fdbserver/backupworker/include/fdbserver/backupworker/BackupWorker.h

## Purpose
This header publishes the classic backup worker actor to other fdbserver components while hiding the implementation details in `BackupWorker.cpp`.

## Important APIs and Types
The header forward-declares `InitializeBackupRequest` and `ServerDBInfo`, includes `BackupInterface` and Flow primitives, and declares:

`Future<Void> backupWorker(BackupInterface bi, InitializeBackupRequest req, Reference<AsyncVar<ServerDBInfo> const> db);`

The parameters carry the worker interface endpoints, the recruitment request containing tag/version/epoch details, and a live async view of database server information.

## Control Flow and Integration
Callers start this actor when the cluster controller or master recruits a classic backup worker. The returned future represents the worker lifetime and can complete normally for an old epoch, be cancelled, or fail with non-shutdown errors.

## State, Risks, and Test Signals
The header stores no state. Its risk is ABI/API coupling: changes to the function signature require all recruitment sites to update. It also intentionally keeps request and DB-info types forward-declared, limiting include fanout. Build/link tests in the backupworker CMake target verify that the declaration and implementation stay linked.
