## sources/user-network-fs/blobfuse2/component/xload/stats_manager.go

Purpose: Aggregates and periodically exports xload progress, throughput, directory, transfer, and disk I/O statistics.

Important APIs and flow: `NewStatsManager` creates a buffered stats channel and optional JSON output file under the default work directory. `Start` initializes JSON with an array skeleton and launches `statsProcessor` plus `statsExporter`. `AddStats` sends `StatsItem`s. `statsProcessor` updates counters by component: lister increments total and directory counts, splitter updates success/failure or disk bytes, data manager tracks downloaded/uploaded bytes, and stats-manager items trigger `calculateBandwidth`. `statsExporter` ticks every four seconds. `calculateBandwidth` logs completion, pending files, Mbps, disk speed, and block pool details, and appends JSON samples.

State and persistence: State is in in-memory counters and optional `xload_stats_{PID}.json`. `Stop` closes channels and waits for the processor.

Dependencies and integration: Receives stats from lister, splitter, data manager, and block pool. Uses JSON append-by-seeking before the final `]`.

Risks: `AddStats` after `Stop` will panic on closed channel. Sending `done` from both `Stop` and `calculateBandwidth` can race. Counters are not atomic but are confined to processor goroutine. Tests cover export and mixed stats.
