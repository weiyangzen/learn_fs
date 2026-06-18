# sources/storage-engines/foundationdb/fdbserver/ratekeeper/TagThrottler.h

Purpose: declares the tag throttling abstraction used by `Ratekeeper`, allowing implementation hiding through `PImpl` and test substitution through `ITagThrottler`.

Important APIs and types: `ITagThrottler` exposes monitoring, request accounting, change id, client rate export, auto/manual/busy counters, auto-throttling enabled state, storage-server auto-throttle updates, and `updateThrottling`. `TagThrottler` implements the interface via `PImpl<TagThrottlerImpl>`.

Control flow, state, and persistence: no direct state is visible except the opaque implementation pointer. Persistence is implementation-defined in `TagThrottler.cpp`, where FDB system keys are watched and updated.

Dependencies and integration: includes `Ratekeeper.h` for `StorageQueueInfo`, tag throttle maps, and Flow futures. Ratekeeper holds `std::unique_ptr<ITagThrottler>` so algorithm code can call the abstraction.

Risks and test signals: risks are interface drift between ratekeeper and implementation, the no-op default `updateThrottling`, and lifetime errors through the PImpl. Tests can substitute `ITagThrottler` to verify ratekeeper behavior without database watches and should assert forwarding of counters and client rates.
