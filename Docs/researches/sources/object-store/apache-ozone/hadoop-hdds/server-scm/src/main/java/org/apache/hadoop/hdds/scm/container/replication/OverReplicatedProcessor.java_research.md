# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/container/replication/OverReplicatedProcessor.java

Purpose: `OverReplicatedProcessor` is the queue worker for over-replicated containers. It extends `UnhealthyReplicationProcessor` with the over-replication queue type and delegates command creation to `ReplicationManager`.

Important APIs and behavior: `dequeueHealthResultFromQueue` calls `ReplicationQueue.dequeueOverReplicatedContainer`; `requeueHealthResult` re-enqueues over-replicated results; `inflightOperationLimitReached` always returns false because delete operations have no global in-flight limit; `sendDatanodeCommands` calls `replicationManager.processOverReplicatedContainer`.

Control flow: the superclass owns the processing loop, interval sleeping, exception handling, and requeue behavior. This subclass only selects the over-replication queue and dispatch method.

State and persistence: it has no state beyond superclass state. Queue entries live in `ReplicationQueue`; pending delete commands are recorded when selected handlers call `ReplicationManager.sendDatanodeCommand`.

Dependencies and integration: constructed by `ReplicationManager` with the over-replicated interval supplier. It integrates with EC, Ratis, and quasi-closed stuck over-replication handlers through `ReplicationManager.processOverReplicatedContainer`.

Risks: no global limit for delete operations means per-datanode delete throttling is the only guard against excessive delete command load. If requeue behavior in the superclass treats all IO exceptions equally, overloaded delete targets can cause repeated retries until datanode command counts drop.

Test signals: `TestOverReplicatedProcessor` covers queue selection, requeue behavior, lack of global in-flight limit, and delegation to `ReplicationManager`.
