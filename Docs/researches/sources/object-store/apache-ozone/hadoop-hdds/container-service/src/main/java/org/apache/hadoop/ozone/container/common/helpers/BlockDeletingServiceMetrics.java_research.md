# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/helpers/BlockDeletingServiceMetrics.java

## Purpose
Metrics holder for the datanode background block deletion service.

## Important APIs, Types, And Functions
Singleton-style static `create`/`unRegister` manage registration. Counters/gauges track successful and failed deletes, bytes deleted, out-of-order transactions, pending block counts/bytes, received transactions/retries/containers/blocks, marked/chosen blocks/containers, lock timeouts, and processed transaction success/failure counts.

## Control Flow
The block deleting service creates the metrics source, updates counters and gauges as it receives and processes delete transactions, and can render a tab-separated summary through `toString`.

## State And Persistence
Metrics live in `DefaultMetricsSystem`; a static `instance` tracks registration. Values are mutable Hadoop metrics objects.

## Dependencies And Integration Points
Depends on Hadoop metrics annotations/system and `BlockDeletingService` for source naming.

## Risks
Static singleton registration can conflict in multi-service tests if unregister is missed. Some variables named gauges are incremented rather than set, so semantic consistency depends on caller usage.

## Test Signals
Signals include registration/unregistration, counter increments during successful/failed deletes, pending gauge updates, lock-timeout count, and summary string values.
