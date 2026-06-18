# sources/storage-engines/foundationdb/bindings/java/src/integration/com/apple/foundationdb/SidebandMultiThreadClientTest.java

## Purpose
This standalone multi-client workload tests causal consistency between a committed database write and a sideband JVM queue message: a consumer should see the key after the producer commits and then enqueues the key name.

## Important APIs, Types, and Functions
It defines static `db2Queues`, nested `Producer`, nested `Consumer`, and setup/process/check helpers. It uses `BlockingQueue`, `LinkedBlockingQueue`, `ThreadLocalRandom`, `Database.run`, tuple encoding, and JUnit assertions.

## Control Flow
`main` configures external client threading, opens all databases, creates one queue per database, starts producer threads for every database, then starts consumer threads and joins consumers. Each producer commits `txnCnt` random keys and offers each key to the queue after commit. Consumers take keys, read them in transactions, and fail if any read returns null.

## State and Persistence Behavior
The test writes many random tuple keys under `Sideband/Multithread/Test/<suffix>` and does not clear them. Queue state is in-memory per database.

## Dependencies and Integration Points
It depends on external-client multi-cluster setup, Java thread scheduling, transaction commit visibility, and tuple packing. Like other multi-client workloads here, it is main-driven rather than a JUnit test method.

## Risks and Edge Cases
Producers are not joined, while each consumer expects exactly `txnCnt` keys. With five producers and five consumers per database, aggregate counts happen to match, but slow producers can make consumers block indefinitely. Random keys are not namespaced by run id and may collide rarely. The consumer decodes the value but does not assert it equals `"bar"`.

## Test Signals
Passing indicates that once a producer's `Database.run` returns, subsequent consumer transactions in the same database handle set can observe the committed key when driven by an out-of-band Java queue.
