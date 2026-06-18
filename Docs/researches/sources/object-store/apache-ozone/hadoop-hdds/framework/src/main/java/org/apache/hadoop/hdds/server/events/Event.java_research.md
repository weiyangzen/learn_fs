# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/Event.java

## Purpose

`Event<PAYLOAD>` identifies an asynchronous event type in the HDDS server event framework.

## Important APIs, Types, and Functions

`getPayloadType()` returns the Java class of the event payload. `getName()` returns a human-readable name for thread names and monitoring.

## Control Flow

The event queue uses event identity and payload type metadata to route payloads to compatible handlers and executors.

## State and Persistence Behavior

The interface defines no state or persistence. Implementations are usually enum-like constants or small descriptor objects.

## Dependencies and Integration Points

It integrates with `EventQueue`, `EventHandler`, `EventPublisher`, and `EventExecutor` in the same server event package.

## Risks and Edge Cases

Incorrect payload type declarations can cause handler cast errors or missed validation. Non-unique names can make metrics/thread diagnostics ambiguous.

## Test Signals

Test event registration with matching/mismatched payload types and monitoring names in queue/executor diagnostics.
