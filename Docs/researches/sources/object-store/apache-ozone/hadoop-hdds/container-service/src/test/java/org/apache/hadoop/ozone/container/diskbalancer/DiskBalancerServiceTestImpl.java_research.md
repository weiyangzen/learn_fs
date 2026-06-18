# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/diskbalancer/DiskBalancerServiceTestImpl.java

## Purpose
Test-only `DiskBalancerService` subclass that replaces periodic scheduling with latch-controlled execution for deterministic service tests.

## Important APIs, Types, And Functions
Constructors delegate to the superclass with zero service timeout. `runBalanceTasks`, `isStarted`, `getTimesOfProcessed`, overridden `start`, and `shutdown` provide test control.

## Control Flow
`start()` creates a daemon thread that repeatedly waits on a latch, submits a `PeriodicalTask`, waits for completion, and increments a processed counter. `shutdown()` interrupts the control thread and calls the superclass.

## State And Persistence
State is in-memory latch, thread, futures, and processed counter. No persistence is added.

## Dependencies And Integration Points
Used by disk balancer service tests to drive superclass logic without real interval waits.

## Risks And Edge Cases
`runBalanceTasks` throws if called after latch count reaches zero. Long future timeout can delay failures if a task hangs.

## Test Signals
Tests observe started state, processed count, and deterministic task execution.
