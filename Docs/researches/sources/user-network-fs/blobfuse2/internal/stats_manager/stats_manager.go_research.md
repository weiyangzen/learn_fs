<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/internal/stats_manager/stats_manager.go -->
# sources/user-network-fs/blobfuse2/internal/stats_manager/stats_manager.go

## Purpose
Implements Blobfuse2 component stats/event collection for the health monitor path. It accepts asynchronous component events and counters, writes event records to a transfer named pipe, and responds to polling-pipe requests by sending changed aggregate stats.

## Important APIs, Types, and Functions
`StatsCollector` owns a buffered channel, worker wait group, and component index. `PipeMsg` is the JSON payload written to the monitor pipe. `Events`, `Stats`, and `ChannelMsg` represent internal event/stat messages. `NewStatsCollector` registers a component stats slot and starts goroutines when `common.MonitorBfs()` is enabled. `PushEvents` sends per-operation event records. `UpdateStats` sends aggregate stat updates. `statsDumper` consumes collector messages, writes events, and updates aggregate stats. `statsPolling` listens on `common.PollingPipe` and writes changed component stats to `common.TransferPipe`. `createPipe` creates FIFOs. `disableMonitoring` clears `common.EnableMonitoring`.

## Control Flow and State
Global `stMgrOpt` stores `statsList`, component last-transfer timestamps, `pollStarted`, and three mutexes. A collector appends a `PipeMsg` slot under `statsMtx`, records its component index, then starts `statsDumper`; the first collector also starts `statsPolling`. Events are copied into a new map before channeling. If the channel is full, the oldest message is dropped. `statsDumper` creates and opens the transfer pipe, marshals event messages immediately, and applies `Increment`, `Decrement`, or `Replace` operations to the component's aggregate value map. `statsPolling` waits for lines containing `"Poll at"`, then sends only components whose timestamp changed since the last poll.

## Dependencies and Integration Points
Depends on `common.MonitorBfs`, `common.TransferPipe`, `common.PollingPipe`, `common.EnableMonitoring`, and `common/log`. Integrates with external `bfusemon`/health monitor processes via named pipes and JSON lines. Component code integrates through `NewStatsCollector`, `PushEvents`, and `UpdateStats`.

## Risks and Edge Cases
Opening a FIFO for write can block if no reader exists; both `statsDumper` and `statsPolling` open `TransferPipe` as write-only. The channel-full path uses `len(sc.channel) == cap(sc.channel)` then receives one item, which is not atomic with other goroutines and can block if the channel is drained concurrently. `UpdateStats` assumes increment/decrement values and existing numeric values are `int64`; wrong types panic. `Destroy` closes the channel but callers can still panic if they push after destroy. `pollStarted` is never reset, so once polling exits due to an error, later collectors will not restart it. Monitoring is globally disabled on many pipe errors.

## Test Signals
This file needs integration tests with FIFOs or abstracted pipe writers to validate event JSON, stat aggregation, poll filtering, and failure behavior. Race testing would be valuable because it combines channels, global state, and mutexes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/internal/stats_manager/stats_manager.go -->
