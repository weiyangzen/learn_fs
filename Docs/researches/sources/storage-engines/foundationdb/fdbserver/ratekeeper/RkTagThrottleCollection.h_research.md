# sources/storage-engines/foundationdb/fdbserver/ratekeeper/RkTagThrottleCollection.h

Purpose: declares the non-copyable ratekeeper tag throttle collection and its private data records.

Important APIs and types: `RkTagData` stores per-tag request-rate smoothing. `RkTagThrottleData` stores a `ClientTagThrottleLimits`, smoothed client rate, creation/update/reduction timestamps, and rate initialization state. Public methods are `autoThrottleTag`, `manualThrottleTag`, `getManualTagThrottleLimits`, `getClientRates`, `addRequests`, throttle counters, and `incrementBusyTagCount`.

Control flow, state, and persistence: this header defines in-memory throttle state only. Move construction/assignment transfers all maps. It has no durable ownership and no direct transaction API.

Dependencies and integration: uses `TransactionTagMap`, prioritized throttle maps, `Smoother`, transaction priorities, and `TagThrottledReason`. `TagThrottler` is the only production wrapper that connects it to database watches and throttle API calls.

Risks and test signals: risks are hidden invariants around positive busyness, valid future expirations, and smoothing windows from client knobs. Tests should validate move semantics, count methods, manual limit lookup, and behavior when `autoThrottlingEnabled` is false.
