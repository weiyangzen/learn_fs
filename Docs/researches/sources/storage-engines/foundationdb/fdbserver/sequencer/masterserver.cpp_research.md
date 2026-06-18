# sources/storage-engines/foundationdb/fdbserver/sequencer/masterserver.cpp

Purpose: implements the master/sequencer actor that assigns monotonically increasing commit-version ranges to commit proxies and publishes live committed version state to readers.

Important APIs and functions: `figureVersion` keeps versions close to wall-clock time while bounding advancement. `getVersion` serializes requests per proxy request number, suppresses duplicates, advances version, and embeds resolver changes. `LiveCommittedVersionServer` handles get/report live committed version requests, including version-vector deltas and waiting for previous versions when needed. `updateRecoveryData` installs epoch/recovery versions, proxy/resolver lists, reference version, and locality. `masterServer` validates cluster-controller identity, composes actors, and exits on lifetime mismatch or normal master errors.

Control flow, state, and persistence: state is in-memory `MasterData`. Recovery data arrives over RPC from recovery machinery; this file does not write disk. Duplicate reply maps are pruned by `mostRecentProcessedRequestNum`.

Dependencies and integration: integrates `MasterInterface`, commit proxies, resolvers via `ResolutionBalancer`, `ServerDBInfo`, cluster controller, version vectors, debug version timestamps, and Flow actor collections.

Risks and test signals: risks include version gaps from clock bugs, request-number ordering stalls, duplicate reply memory growth, live committed version ordering, and forced-recovery locality. Tests cover `figureVersion`; broader signals are master counters, version-vector samples, `MasterTerminated` reasons, and commit proxy progress.
