<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHADBTransactionBuffer.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHADBTransactionBuffer.java

## Purpose

`SCMHADBTransactionBuffer` defines the HA transaction-buffer contract for batching SCM DB writes, tracking the latest transaction info, and coordinating snapshot/flush state while applying Ratis transactions.

## Important APIs, Types, and Functions

It extends `DBTransactionBuffer` and adds `updateLatestTrxInfo`, `getLatestTrxInfo`, `getLatestSnapshot`, `setLatestSnapshot`, `getLatestSnapshotRef`, `flush`, `flushIfNeeded`, `shouldFlush`, `init`, `beginApplyingTransaction`, and `endApplyingTransaction`.

## Control Flow

Implementations buffer table puts/deletes inherited from `DBTransactionBuffer`, update latest transaction metadata, flush batches to RocksDB, expose latest Ratis snapshot info, and suppress periodic flushes while transactions are actively being applied.

## State and Persistence Behavior

The interface specifies persistent behavior: flush must commit DB batch contents and transaction info. Snapshot references are in-memory but reflect persisted transaction positions.

## Dependencies and Integration Points

It integrates SCM metadata mutations with Ratis state machine apply, snapshot installation, transaction monitoring tasks, and checkpoint serving.

## Risks and Edge Cases

Implementations must keep transaction info in the same batch as data mutations or snapshots can advertise uncommitted state. Apply counters must be balanced to avoid starving flushes.

## Test Signals

Implementation tests should verify batch commit atomicity, transaction info monotonicity, flush-if-needed timing, suppression during active apply, snapshot reference updates, and reinitialization after snapshot install.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHADBTransactionBuffer.java -->
