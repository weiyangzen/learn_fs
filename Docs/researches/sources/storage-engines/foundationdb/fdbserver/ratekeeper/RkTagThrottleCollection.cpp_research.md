# sources/storage-engines/foundationdb/fdbserver/ratekeeper/RkTagThrottleCollection.cpp

Purpose: implements the in-memory collection that merges manual and automatic transaction tag throttles and computes smoothed client-facing tag rates.

Important APIs and functions: `RkTagThrottleData::getTargetRate` and `updateAndGetClientRate` translate limits plus observed request rate into smoothed client rates. `computeTargetTpsRate` calculates target TPS from current and desired tag busyness. `autoThrottleTag` creates or updates automatic throttles with aggregation/update windows. `manualThrottleTag` installs priority-specific manual throttles. `getClientRates` expires old entries, merges manual and auto throttles per priority, applies auto ramp-up, and returns `PrioritizedTransactionTagMap`. `addRequests` feeds request-rate smoothing.

Control flow, state, and persistence: state is process-local maps of auto throttles, manual priority maps, request-rate smoothers, and busy-read/write counters. Persistence is external: `TagThrottler` reads/writes system tag throttle keys and rebuilds this collection.

Dependencies and integration: depends on tag throttle client types, `CLIENT_KNOBS`, `SERVER_KNOBS`, transaction priorities, and TraceEvent/CODE_PROBE. Used only behind `TagThrottler`.

Risks and test signals: risks include erasing while iterating manual throttle maps, infinite-rate sentinel handling, divide-by-zero if busyness/request-rate invariants are violated, and priority override mistakes. Tests should cover expiration, ramp-up, manual-vs-auto precedence, max auto throttle count, and request-rate smoothing.
