# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneRepairShell.java

## Purpose
`TestOzoneRepairShell` validates repair-shell commands for updating OM/SCM transaction-info tables offline and triggering OM quota repair/status operations online.

## Important APIs, Types, and Functions
The test uses `OzoneRepair().getCmd()`, `OzoneDebug().getCmd()`, `TransactionInfoRepair.getColumnFamily(Component)`, `RepairTool.Component` values OM and SCM, `OMStorage.getOmDbDir`, `ServerUtils.getScmDbDir`, and confirmation input through `withTextFromSystemIn`. It parses transaction info with regex `([0-9]+#[0-9]+)`.

## Control Flow, State, and Persistence
For each component, the test stops OM and SCM, scans the transaction-info column family with debug `ldb`, records the original highest term/index, runs `om|scm update-transaction --db --term 1111 --index 1111`, verifies stdout and DB scan reflect the update, restores the original term/index, restarts OM, and creates a volume to verify service usability. The quota test checks status, runs dry-run start, confirms status lacks `lastRun`, then runs real quota repair and polls status for completion output.

## Dependencies and Integration Points
This integrates offline repair CLI, debug RocksDB scanner, OM and SCM DB path discovery, transaction-info column families, mini-cluster restart, object-store client operations, and quota repair service endpoints.

## Risks and Test Signals
Risks include regex coupling to ldb output, needing services stopped for DB mutation, stdout text brittleness, and a likely fragile quota completion predicate. Signals include DB scan content before/after repair, successful restoration and OM restart, volume creation after repair, command exit codes, and quota status output changes.
