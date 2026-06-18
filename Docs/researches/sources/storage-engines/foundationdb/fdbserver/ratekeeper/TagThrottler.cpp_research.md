# sources/storage-engines/foundationdb/fdbserver/ratekeeper/TagThrottler.cpp

Purpose: bridges durable tag throttle system keys, automatic throttle creation, expired throttle cleanup, and the in-memory `RkTagThrottleCollection` consumed by ratekeeper.

Important APIs and functions: `TagThrottlerImpl::monitorThrottlingChanges` reads `tagThrottleKeys`, `tagThrottleAutoEnabledKey`, writes the manual-throttle limit key on first successful pass, converts duration-style expirations to absolute timestamps, rebuilds throttle collection state, watches `tagThrottleSignalKey`, and bumps a change id. `tryUpdateAutoThrottling` creates automatic throttles through `ThrottleApi::throttleTags`. `cleanupExpiredTagThrottles` runs periodically through `recurring`. The public `TagThrottler` forwards `addRequests`, `getClientRates`, counters, and `tryUpdateAutoThrottling(StorageQueueInfo)`.

Control flow, state, and persistence: local state is `RkTagThrottleCollection`, change id, auto-enabled flag, and cleanup future. Durable state lives in FDB system keys managed with lock-aware, system-immediate transactions and `ThrottleApi`.

Dependencies and integration: depends on `Database`, tag throttle key codecs, `StorageQueueInfo` busiest tags, ratekeeper knobs, and the ratekeeper proxy reply path. It also uses storage queue/durability lag thresholds to decide when read/write busy tags deserve auto-throttle attempts.

Risks and test signals: risks include stale throttle state between watch signals, invalid auto-enabled values, too many system keys for `TOO_MANY`, and racey duration-to-expiration conversion. Signals are `RatekeeperReadThrottledTags`, `RatekeeperThrottleSignaled`, auto/manual throttle traces, and client proxies receiving updated tag maps when change id advances.
