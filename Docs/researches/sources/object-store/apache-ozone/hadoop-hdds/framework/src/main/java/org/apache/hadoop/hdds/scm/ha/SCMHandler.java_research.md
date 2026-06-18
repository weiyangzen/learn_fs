# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHandler.java

## Purpose

`SCMHandler` is a base interface for SCM handlers participating in Ratis-backed HA request processing.

## Important APIs, Types, and Functions

It defines one method, `getType()`, returning an `SCMRatisProtocol.RequestType`.

## Control Flow

No implementation. Dispatcher code can use `getType()` to route or register handlers by Ratis request type.

## State and Persistence Behavior

No state or persistence.

## Dependencies and Integration Points

It depends on generated `SCMRatisProtocol.RequestType` and integrates with SCM HA/Ratis command handlers.

## Risks and Test Signals

Handler type uniqueness is enforced outside this interface. Tests should verify registrations do not collide and handlers report the expected request type.
