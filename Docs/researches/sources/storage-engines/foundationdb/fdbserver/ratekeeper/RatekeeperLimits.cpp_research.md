# sources/storage-engines/foundationdb/fdbserver/ratekeeper/RatekeeperLimits.cpp

Purpose: implements the `RatekeeperLimits` constructor and binds per-priority ratekeeper limit state to metric names and TraceEvent cache keys.

Important APIs and functions: `RatekeeperLimits::RatekeeperLimits` initializes `tpsLimit`, metric handles for TPS and limit reason, storage and log target/spring bytes, max version difference, durability lag target/state, priority, context string, and `EventCacheHolder` for update traces. Context differentiates default and batch limit metric names.

Control flow, state, and persistence: no runtime loop or persistent state exists in this file. It only initializes an in-memory configuration object from constructor arguments and global metric registration.

Dependencies and integration: depends on `Ratekeeper.h`, metric handles, transaction priority naming, and ratekeeper update logging in `Ratekeeper::updateRate`. `Ratekeeper.cpp` creates default and batch instances with different knobs.

Risks and test signals: risks are mismatched metric names, wrong default `durabilityLagLimit` initialization, or swapped default/batch knob values. Test signals are metrics appearing under expected names and correct limit/reason updates in ratekeeper traces.
