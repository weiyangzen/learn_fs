# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/main/java/org/apache/hadoop/hdds/scm/cli/container/ReconcileSubcommand.java

## Purpose
Implements `ozone admin container reconcile`, triggering replica checksum reconciliation or reporting reconciliation status.

## Important APIs, Types, And Functions
Options include `ContainerIDParameters` and `--status`. Trigger mode calls `ScmClient.reconcileContainer`. Status mode calls `getContainer`, validates closed Ratis containers, fetches replicas, and writes `ContainerWrapper` JSON through `SequenceWriter`. Nested wrappers expose datanode identity, replica state/index, and checksum with `JsonUtils.ChecksumSerializer`.

## Control Flow
`execute` branches on `--status`. Trigger mode loops IDs, prints successes, accumulates failures, and throws if any failed. Status mode validates all IDs first, streams status objects, buffers human-readable errors until JSON is flushed, and throws if any container failed.

## State And Persistence
Trigger mode mutates datanode/container reconciliation workflow state. Status mode is read-only.

## Dependencies And Integration Points
Depends on SCM reconciliation RPCs, `ContainerInfo`, `ContainerReplicaInfo`, Jackson annotations, `JsonUtils`, and Ozone access-control formatting.

## Risks And Test Signals
Status is client-side limited to non-open Ratis containers; future EC support requires updates. `getExceptionMessage` assumes non-null messages. Tests should cover open/EC containers, partial failures, checksum match calculation, authentication failures, JSON array validity, and trigger failure exit status.
