# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/ozone/protocol/commands/RetriableDatanodeEventWatcher.java

Purpose: This event watcher retries datanode commands that have a lease timeout before completion. It watches a command start event and a command-status completion event, and requeues timed-out commands onto SCM's retriable datanode command event.

Important APIs and types: The generic type parameter `T extends CommandStatusEvent`. The constructor takes `Event<CommandForDatanode>`, `Event<T>`, and `LeaseManager<Long>` and passes them to `EventWatcher`. It overrides `onTimeout` and `onFinished`.

Control flow: The inherited watcher starts a lease when a command is fired and completes it when a matching completion event arrives. If the lease times out, `onTimeout` logs command type and ID, then fires `SCMEvents.RETRIABLE_DATANODE_COMMAND` with the original `CommandForDatanode` payload. `onFinished` intentionally does nothing after normal completion.

State and persistence behavior: Durable state is not stored here. Runtime retry state is managed by the inherited `EventWatcher` and `LeaseManager`. Retried commands flow back through SCM event processing and node command queues.

Dependencies and integration points: It integrates command status reporting, SCM event publication, command leases, and retriable datanode command dispatch. It is relevant for commands where SCM expects eventual datanode acknowledgement and wants timeout-based retry.

Risks: Timeout retry can duplicate commands if completion races with lease expiration or if datanodes eventually execute an old command. The class assumes `CommandForDatanode.getId` matches completion event IDs managed by the base watcher. `onFinished` has no cleanup beyond inherited lease handling.

Test signals: Tests should assert timed-out commands are re-fired as `RETRIABLE_DATANODE_COMMAND`, completion suppresses retry, log fields are safe for null command details, and duplicate/race behavior is acceptable for idempotent datanode commands.
