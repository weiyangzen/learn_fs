# sources/storage-engines/foundationdb/fdbserver/sequencer/ResolutionBalancer.cpp

Purpose: implements resolver key-range load balancing by sampling resolver metrics and sending move instructions to commit proxies through commit-version replies.

Important APIs and functions: `setResolvers` records resolver interfaces and triggers balancing when more than one resolver exists. `setChangesInReply` attaches pending `ResolverMoveRef` changes to the next reply for each commit proxy. `findRange` selects a source resolver range to move, preferring existing borders with the destination, then new borders, then any source range. `resolutionBalancing_impl` periodically gathers `ResolutionMetricsReply`, compares max/min load, asks the source resolver to split a range, updates the local `CoalescedKeyRangeMap`, and publishes changes for proxies.

Control flow, state, and persistence: state is in-memory resolver assignment, pending changes, target proxy set, and change version. There is no durable state; proxies learn moves via sequencer replies and future recovery can rebuild assignment.

Dependencies and integration: uses `ResolverInterface` metrics/split RPCs, `CommitProxyInterface`, `GetCommitVersionReply`, `KeyRangeMap`, `IndexedSet`, and sequencer version pointer from `MasterData`.

Risks and test signals: risks are moving already-pending ranges, bad split estimates, starvation while pending changes are not consumed, and assignment drift after resolver changes. Signals are `MovingResolutionRange` traces, `resolverChangesVersion`, balanced resolver metrics, and proxy receipt of resolver changes.
