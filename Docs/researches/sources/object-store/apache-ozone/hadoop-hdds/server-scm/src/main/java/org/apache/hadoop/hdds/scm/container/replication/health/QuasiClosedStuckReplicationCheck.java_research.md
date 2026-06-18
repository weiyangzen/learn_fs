<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/QuasiClosedStuckReplicationCheck.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/QuasiClosedStuckReplicationCheck.java

## Purpose

`QuasiClosedStuckReplicationCheck` applies special replication rules to quasi-closed Ratis containers that cannot be force-closed. It tries to preserve several copies of the highest-BCSID origin and fewer copies of other origins rather than applying ordinary Ratis replica-count rules.

## Important APIs, Types, and Functions

Important methods are static `shouldHandleAsQuasiClosedStuck`, `handle`, and private `hasEnoughOriginsWithOpen`. It uses `QuasiClosedStuckReplicaCount`, configuration values `getQuasiClosedStuckBestOriginCopies` and `getQuasiClosedStuckOtherOriginCopies`, and combined health states such as `QUASI_CLOSED_STUCK_UNDER_REPLICATED`.

## Control Flow

The static gate requires a quasi-closed container, force-close-stuck status, more than the single-origin normal case, and not enough open/quasi-closed origins waiting to close naturally. `handle` reports stuck-missing when no replicas exist. Otherwise it builds a configured replica counter, skips all-unhealthy cases, counts pending adds/deletes, reports under or over replication, and enqueues only if the corresponding pending operation type is absent.

## State and Persistence Behavior

It owns no state beyond configuration. It samples reports and enqueues transient repair work; persistent changes happen later via normal command processors.

## Dependencies and Integration Points

It integrates with `QuasiClosedContainerHandler`, `QuasiClosedStuckReplicaCount`, ReplicationQueue, and Ratis health handling, which explicitly defers when this special handler applies.

## Risks and Edge Cases

The static gate uses default copy counts for initial origin counting, while `handle` uses configured counts. Pending-op suppression is coarse by add/delete count, not target quality. All-unhealthy stuck containers are intentionally handled by another handler.

## Test Signals

Tests should cover the static gate, single-origin fallback to normal handler, open-origin suppression, missing no-replica report, under/over queueing without pending ops, queue suppression with pending ops, configured copy counts, and all-unhealthy pass-through.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/health/QuasiClosedStuckReplicationCheck.java -->
