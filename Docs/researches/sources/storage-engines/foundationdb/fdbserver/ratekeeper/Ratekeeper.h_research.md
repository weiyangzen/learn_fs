# sources/storage-engines/foundationdb/fdbserver/ratekeeper/Ratekeeper.h

Purpose: declares internal ratekeeper data structures and the `Ratekeeper` class used by the implementation target.

Important APIs and types: `StorageQueueInfo` stores smoothed durable bytes, input bytes, versions, disk space, locality, accepting state, busiest read/write tags, and commit-cost estimations. `TLogQueueInfo` tracks smoothed tlog durability, input, and disk metrics. `RatekeeperLimits` holds per-priority target/spring bytes, max version difference, durability lag controls, TPS metric handles, priority, and TraceEvent cache. `Ratekeeper` owns the database, server/tlog maps, smoothing history, proxy info, health metrics, and a polymorphic `ITagThrottler`.

Control flow, state, and persistence: this header defines in-memory state only. Persistence and watches are handled in `Ratekeeper.cpp` through FDB transactions and tag throttle APIs.

Dependencies and integration: includes database context, storage-server and tlog interfaces, tag throttling, `Smoother`, ratekeeper interface, and limit reason enums. It is private to the ratekeeper library except for local implementation consumers.

Risks and test signals: risks are stale values in `lastReply`, smoothing semantics when server instances restart, integer/double conversion in queue and durability calculations, and constructor knob drift. Tests should exercise `StorageQueueInfo` update/reset behavior, `getTagThrottlingRatio`, limit metric initialization, and tlog/storage queue accessors.
