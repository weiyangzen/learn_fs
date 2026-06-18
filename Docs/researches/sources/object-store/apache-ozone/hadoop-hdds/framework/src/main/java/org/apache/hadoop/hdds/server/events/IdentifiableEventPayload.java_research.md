# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/server/events/IdentifiableEventPayload.java

Purpose: `IdentifiableEventPayload` marks event payloads that have a stable long id. It is the identity contract for `EventWatcher` start and completion correlation.

Important APIs/types/functions: the only method is `getId()`.

Control flow: `EventWatcher` stores timeout payloads by id, acquires/releases leases by id, and matches completion payload ids to started payloads. Subclasses receive the original start payload in `onTimeout()` or `onFinished()`.

State and persistence: no state in the interface. Implementations must provide an id that remains stable across hash/equals lifecycle and across the related start/completion events.

Dependencies/integration: used as generic bounds for `EventWatcher<TIMEOUT_PAYLOAD, COMPLETION_PAYLOAD>`.

Risks: duplicate ids collapse tracking state. Completion events with ids that have already timed out are logged as missing leases. Id reuse before old state is cleared can cause mis-correlated completion or timeout behavior.

Test signals: `TestEventWatcher` defines simple identifiable payloads for under-replication and replication-completion flows and verifies correlation behavior.
