# Research: sources/sync-backup/syncthing/lib/watchaggregator/aggregator.go

## sources/sync-backup/syncthing/lib/watchaggregator/aggregator.go

Purpose: coalesces raw filesystem watcher events into bounded scan path batches, delaying noisy changes and ordering removes after non-removes when useful.

Important APIs/types/functions: public `Aggregate`; internal `aggregator`, `eventDir`, `aggregatedEvent`, `eventCounter`, `newAggregator`, `mainLoop`, `newEvent`, `aggregateEvent`, `actOnTimer`, `notify`, `popOldEventsTo`, `isOld`, `CommitConfiguration`, and `notifyTimeout`. Tunables `maxFiles` and `maxFilesPerDir` cap event fan-out.

Control flow: `mainLoop` listens to fs events, config updates, in-progress item events, timer firings, and context cancellation. `aggregateEvent` stores paths in a tree, collapses overfull directories to parent paths, and collapses global overflow or `"."` to a full-folder scan. Timer handling pops old events, optionally releases remaining remove events early when only removes remain, and sends batches asynchronously in NonRemove, Mixed, Remove order.

State and persistence: all state is in-memory: event tree, counters, timers, in-progress path set, and folder config. No disk persistence.

Dependencies and integration: connects `lib/fs.Event`, `lib/config.Wrapper` subscriptions, `lib/events` item lifecycle events, and model scan scheduling via the output channel. Risks include timing flakiness, channel backpressure, stale in-progress tracking, and path normalization across platforms. Unit tests cover aggregation caps, delays, remove ordering, and in-progress filtering.
