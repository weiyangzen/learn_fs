<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/events/EventHandlerStub.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/events/EventHandlerStub.java

Purpose: simple test helper that records received events for assertions in event-system tests.

Important APIs/types/functions: implements `EventHandler<PAYLOAD>`, stores `List<PAYLOAD> receivedEvents`, implements `onMessage(PAYLOAD, EventPublisher)`, and exposes `getReceivedEvents`.

Control flow: when the event queue invokes `onMessage`, the payload is appended to an in-memory list. Tests later inspect that list.

State and persistence behavior: state is only the mutable `ArrayList` of received payloads. No synchronization is provided, so callers rely on event queue processing completion before assertions.

Dependencies and integration points: integrates with `org.apache.hadoop.hdds.server.events.EventHandler` and `EventPublisher`; used by watcher/queue tests to avoid repeated mock handlers.

Risks: not thread-safe by itself. If reused in tests with concurrent handler invocation and assertions before queue drain, ordering and visibility could be flaky.

Test signals: helper has no direct tests but provides observable received-event state to sibling tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/server/events/EventHandlerStub.java -->
