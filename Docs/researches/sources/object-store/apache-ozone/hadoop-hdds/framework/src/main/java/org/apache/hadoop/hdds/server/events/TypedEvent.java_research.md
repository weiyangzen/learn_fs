# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/TypedEvent.java

Purpose: `TypedEvent<T>` is a basic `Event<T>` implementation that binds an event name to a payload class.

Important APIs/types/functions: constructors accept `(Class<T> payloadType, String name)` or default the name to `payloadType.getSimpleName()`. `getPayloadType()`, `getName()`, and `toString()` implement the event contract.

Control flow: components declare static `TypedEvent` instances and register handlers against them in `EventQueue`. The event object is the map key, so object identity/equality behavior is inherited from `Object`; the same event instance must be used for registration and publication unless a wrapper implements equality.

State and persistence: immutable in-memory fields only.

Dependencies/integration: implements the local `Event<T>` interface and is heavily used in tests and SCM event declarations.

Risks: no runtime validation confirms payload instances match `payloadType` during `fireEvent()`. Event name participates in executor naming; names containing `For` are rejected by `EventQueue`.

Test signals: `TestEventQueue`, `TestEventQueueChain`, and `TestEventWatcher` instantiate `TypedEvent` directly for unit event streams.
