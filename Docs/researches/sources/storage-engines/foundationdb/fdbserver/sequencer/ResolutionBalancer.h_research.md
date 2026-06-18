# sources/storage-engines/foundationdb/fdbserver/sequencer/ResolutionBalancer.h

Purpose: declares the sequencer-side helper that tracks resolver assignments and pending balancing changes.

Important APIs and types: `ResolutionBalancer` contains `resolverChanges`, `resolverChangesVersion`, `resolverNeedingChanges`, a pointer to `MasterData::version`, commit proxy and resolver interface vectors, and a trigger. Public methods are `resolutionBalancing`, static implementation entry, `setResolvers`, `setCommitProxies`, and `setChangesInReply`.

Control flow, state, and persistence: state is memory-only and scoped to the master actor. Pending resolver changes remain in an `AsyncVar` until every tracked commit proxy receives them.

Dependencies and integration: depends on commit proxy interfaces, resolver interfaces, master reply types, Flow arenas/triggers, and generic actor support. It is included by `MasterData.h` and `masterserver.cpp`.

Risks and test signals: risks are dangling `pVersion`, pending change loss if commit proxy set changes mid-flight, and missing trigger when resolver count crosses one. Tests should cover single resolver no-op, multi-resolver trigger, reply fanout clearing, and version assigned as current master version plus one.
