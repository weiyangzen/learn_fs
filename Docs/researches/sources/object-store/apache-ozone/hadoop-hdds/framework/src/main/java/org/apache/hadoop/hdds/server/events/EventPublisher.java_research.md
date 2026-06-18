# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/EventPublisher.java

Purpose: `EventPublisher` is the producer-facing event bus contract. It abstracts publication so event handlers and components can emit typed events without depending directly on `EventQueue`.

Important APIs/types/functions: `fireEvent(EVENT_TYPE event, PAYLOAD payload)` is generic over payload and event type where `EVENT_TYPE extends Event<PAYLOAD>`. This keeps event identifiers and payload classes paired at compile time.

Control flow: `EventQueue` implements this interface. Handler code receives an `EventPublisher` and can publish additional events, creating asynchronous event chains. Other components may mock this interface in tests when only publication side effects matter.

State and persistence: the interface has no state or persistence. Implementations define queueing, threading, and failure behavior.

Dependencies/integration: consumed by `EventHandler`, `EventWatcher`, SCM handlers, container command handlers, and tests. The main implementation is `EventQueue`.

Risks: because publication is asynchronous in `EventQueue`, callers cannot infer completion from a return. Type safety only applies at compile time; raw types in `EventQueue` internals mean mismatched custom registrations can still cause runtime issues.

Test signals: mocked or real `EventPublisher` instances appear in SCM and container tests; `TestEventQueueChain` verifies follow-on publication from handlers through this contract.
