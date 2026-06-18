# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/utils/SimpleStriped.java

## Purpose
Provides a factory for Guava striped read/write locks with optional fair ordering.

## Important APIs, Types, And Functions
The utility is final with a private constructor. `readWriteLock(int stripes, boolean fair)` returns `Striped<ReadWriteLock>` built with `Striped.custom` and `ReentrantReadWriteLock(fair)`.

## Control Flow
The static factory delegates lock creation to Guava and eagerly returns the striped lock container.

## State And Persistence
The utility owns no state. Lock state lives in returned `ReadWriteLock` instances and is process-local.

## Dependencies And Integration Points
Depends on Guava `Striped`, Java `ReadWriteLock`, and `ReentrantReadWriteLock`. It is used where keyed concurrency control needs lock striping with fairness control.

## Risks
Fair locks can reduce throughput under contention. Stripe count still controls collision rate, so too few stripes serializes unrelated keys. Behavior depends on Guava `Striped.custom` semantics.

## Test Signals
`TestSimpleStriped` verifies lock creation and fairness setting. Additional tests can check stripe stability for equal keys and contention behavior.
