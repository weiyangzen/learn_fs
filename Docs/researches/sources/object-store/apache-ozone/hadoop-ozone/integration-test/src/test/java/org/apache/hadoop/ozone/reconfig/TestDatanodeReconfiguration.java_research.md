# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/reconfig/TestDatanodeReconfiguration.java

## Purpose
`TestDatanodeReconfiguration` validates live reconfiguration of datanode properties, especially block deletion and replication thread pool sizing.

## Important APIs, Types, and Functions
The subject is the first `HddsDatanodeService` reconfiguration handler. It expects keys from `DatanodeConfiguration`, `TracingConfig`, `HDDS_DATANODE_BLOCK_DELETE_THREAD_MAX`, block deleting interval/timeout/workers, and `REPLICATION_STREAMS_LIMIT_KEY`. Behavioral tests call `reconfigureProperty` and then inspect `BlockDeletingService`, `DeleteBlocksCommandHandler` executor, and replication server executor.

## Control Flow, State, and Persistence
The tests run against a non-HA cluster provided by `NonHATests`. They mutate live datanode configuration through the reconfiguration handler and immediately verify in-memory service state: block delete limit, delete-block command executor core/max pool sizes, and replication executor core/max pool sizes. No restart or durable config file rewrite is asserted.

## Dependencies and Integration Points
This file connects the generic reconfiguration framework to datanode container services, command dispatch, block deletion, replication server concurrency, tracing config, and datanode config metadata.

## Risks and Test Signals
Risks include thread pool resizing invariants, invalid deltas producing non-positive pools if defaults change, and expected key drift. The signal is direct in-memory observation after reconfiguration, which is stronger than checking only stored config values.
