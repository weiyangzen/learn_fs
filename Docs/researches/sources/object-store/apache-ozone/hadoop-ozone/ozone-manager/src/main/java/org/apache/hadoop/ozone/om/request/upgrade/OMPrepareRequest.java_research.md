
# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/upgrade/OMPrepareRequest.java

Purpose: Prepares OM for upgrade/downgrade by ensuring committed transactions are flushed, taking a Ratis state-machine snapshot, purging logs, and writing prepare marker state.

Important APIs and types: Extends `OMClientRequest`; uses `PrepareRequestArgs`, `PrepareResponse`, `OMPrepareResponse`, `OzoneManagerDoubleBuffer`, `OzoneManagerRatisServer`, `OzoneManagerStateMachine`, `RaftServer.Division`, `RaftLog`, and `PrepareState.finishPrepare/cancelPrepare`.

Control flow: Validation builds a prepare response with the current transaction index, manually adds it to the double buffer, waits until OM DB and Ratis state machine have applied at least that index, takes a snapshot and purges logs via `takeSnapshotAndPurgeLogs`, writes the prepare marker, audits, and handles failures by returning `PREPARE_FAILED`, cancelling prepare state, and restoring interrupt status when needed.

State and persistence behavior: Mutates double-buffer state, Ratis snapshot/log state, and local prepare marker file. It intentionally bypasses normal cache mutation and manually enqueues its response before log purging.

Dependencies and integration points: Deeply integrates OM request processing with Ratis state machine, DB snapshot index tracking, log purge mechanics, prepare gate state, audit logging, and client-configured wait intervals.

Risks: Timing and ordering are critical; losing the prepare log or snapshot before DB flush could corrupt upgrade state. Concurrent prepare/cancel requests have documented limitations. Tests should cover timeout branches, snapshot index lower than prepare index, purge future failure, marker cleanup on error, and manual double-buffer insertion.
