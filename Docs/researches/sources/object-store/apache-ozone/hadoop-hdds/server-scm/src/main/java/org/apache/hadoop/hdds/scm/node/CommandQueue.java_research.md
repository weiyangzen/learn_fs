# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/CommandQueue.java

Purpose: `CommandQueue` is the SCM-side per-datanode queue of `SCMCommand<?>` objects to be delivered on subsequent datanode heartbeats. It is explicitly not thread-safe, so callers such as `SCMNodeManager` must protect access with their own lock.

Important APIs and types: The public surface includes `addCommand(DatanodeID, SCMCommand<?>)`, `getCommandsInQueue()`, `getDatanodeCommandCount(DatanodeID, Type)`, `getDatanodeCommandSummary(DatanodeID)`, and test-only `clear()`. Package-private `getCommand(DatanodeID)` drains all commands for a datanode. The private `Commands` holder tracks command order plus a `Map<SCMCommandProto.Type, Integer>` summary.

Control flow: Adding a command creates or finds the datanode's `Commands`, appends the command, updates the type summary only when `SCMCommand.contributesToQueueSize()` is true, and increments the global `commandsInQueue`. Draining removes the datanode entry from `commandMap`, returns the previous ordered list, clears per-node summaries, and subtracts the returned list size from the global counter.

State and persistence behavior: All state is in-memory: `commandMap`, per-node command lists, summaries, and the global count. Commands are not persisted in this class, so an SCM restart loses queued commands unless higher layers regenerate them.

Dependencies and integration points: It depends on `DatanodeID`, datanode protocol command types, and Ozone `SCMCommand`. `DeadNodeHandler` clears a dead node's queue through `NodeManager.getCommandQueue`, and heartbeat handling uses queue summaries to merge SCM-side pending commands with datanode-reported queued counts.

Risks: The class relies on external synchronization; unsynchronized callers can corrupt counts or lose commands. `commandsInQueue` counts all drained commands, while summaries omit commands that do not contribute to queue size, so global count and summary totals intentionally differ. Draining subtracts the entire returned list size, so any future non-queued or synthetic command semantics need review.

Test signals: Useful tests should cover FIFO drain order, empty-list behavior, global count reset after drain and clear, type summary copies being caller-safe, non-contributing commands excluded from summaries, and external lock discipline in callers.
