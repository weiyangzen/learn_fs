# sources/storage-engines/foundationdb/fdbserver/worker/MetricLogger.actor.h

## Purpose
This actor header declares the worker metric logging entry points and handles actor-compiler include conventions.

## Important APIs, Types, And Functions
It declares `ACTOR Future<Void> runMetrics(Future<Database> fcx, Key metricsPrefix);` for DB-backed TDMetric persistence and `ACTOR Future<Void> runMetrics();` for UDP process metric emission. It forward-declares `Database` and includes FDB/Flow types.

## Control Flow
No behavior is implemented here. Consumers include the header, and actor-generated code is included under the `NO_INTELLISENSE`/include guard pattern.

## State And Persistence Behavior
The header has no state. Persistence semantics are defined by the DB-backed overload in the `.cpp`.

## Dependencies And Integration Points
It depends on actorcompiler/unactorcompiler conventions and is consumed by worker startup code that launches metric logging.

## Risks And Test Signals
The main risk is actor-compiler include ordering; the `flow/actorcompiler.h` include must remain last before actor declarations and `flow/unactorcompiler.h` must close the block.
