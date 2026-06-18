# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/fs/TestDUOptimized.java

## Purpose

This test class verifies `DUOptimized` delegation and optional container-usage aggregation.

## Important APIs, Types, And Functions

The subject is `DUOptimized`. A mocked `DU` is injected into the private `metaPathDU` field via reflection. Tests call `getUsedSpace`, `setContainerUsedSpaceProvider`, `getCapacity`, and `getAvailable`.

## Control Flow

`setUp()` creates a subject with `/tmp` paths and replaces its internal `DU`. Tests configure mock return values and assert delegation. When a container usage provider is set, used space is the sum of metadata DU usage and the supplied container usage.

## State And Persistence

State is in-memory subject fields and mock behavior. No real filesystem state is measured despite `/tmp` constructor arguments.

## Dependencies And Integration Points

The test integrates with Mockito, reflection, `Supplier<Long>`, production `DU`, and `DUOptimized`.

## Risks

Reflection creates brittle coupling to the private field name `metaPathDU`. The test covers arithmetic and delegation, not exclusion provider path handling or real disk behavior.

## Test Signals

Signals are exact used-space delegation, additive container usage, capacity delegation, and available-space delegation.
