# sources/object-store/minio/cmd/tier-last-day-stats.go

Purpose: maintains rolling 24-hour per-tier transfer statistics for remote tiers. It stores hourly `tierStats` bins and can merge per-node maps for cluster-wide reporting.

Important APIs and types: `lastDayTierStats` contains `[24]tierStats` and `UpdatedAt`. Methods include `addStats`, `forwardTo`, `clone`, and `merge`. `DailyAllTierStats` is a map from tier name to `lastDayTierStats`, with `merge` and `addToTierInfo`.

Control flow: `addStats` forwards the ring buffer to `time.Now`, chooses the current hour index, and adds the incoming stats. `forwardTo` clears bins between the previous update hour and target hour; if 24 or more hours elapsed, it clears all bins. `merge` clones both inputs, forwards the older one to the newer timestamp, and adds corresponding bins. `DailyAllTierStats.addToTierInfo` overlays internal stats onto `madmin.TierInfo.DailyStats`.

State and persistence: this type is in-memory aggregation state, with msgp serialization generated in the companion `_gen.go` file. The 24 fixed bins are hour-of-day indexed, so `UpdatedAt` is required to know which bins are current.

Dependencies and integration points: depends on `tierStats` from MinIO data-usage/tier accounting and `madmin.TierInfo` response structs. `TierStatsHandler` integrates these stats into admin API output.

Risks: because bins are indexed by hour, clock jumps and time-zone assumptions can affect which bins are cleared. `forwardTo` treats any elapsed duration below one hour as no movement, and elapsed durations of 24 hours or more as total expiration. Merge correctness depends on forwarding both nodes to a common timestamp before summing.

Test signals: generated serialization tests cover msgp round trips. Behavioral tests should focus on `forwardTo` clearing boundaries, 24-hour expiration, and merging maps with different `UpdatedAt` values.
