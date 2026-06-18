# sources/storage-engines/rocksdb/java/src/main/java/org/rocksdb/StatisticsCollector.java

## Purpose
`StatisticsCollector` periodically samples one or more `Statistics` instances and invokes user callbacks for every ticker and histogram.

## Important APIs and Types
The constructor takes a `List<StatsCollectorInput>` and a polling interval in milliseconds. `start()` submits the collector loop to a single-thread executor. `shutDown(int)` stops the loop, interrupts executor work, and waits for termination.

## Control Flow
The private `collectStatistics()` runnable loops while `_isRunning`, checks interruption, iterates each input, emits all `TickerType` values except `TICKER_ENUM_MAX`, emits all `HistogramType` values except `HISTOGRAM_ENUM_MAX`, then sleeps for the configured interval. Interrupted sleeps restore interrupt state and exit; other exceptions are wrapped in `RuntimeException`.

## State and Persistence Behavior
State is in-memory: input list, executor, interval, and volatile running flag. The collector does not persist samples; persistence is delegated to callback implementations. Statistics objects must remain live until shutdown finishes.

## Dependencies and Integration Points
It depends on `StatsCollectorInput`, `StatisticsCollectorCallback`, `Statistics`, `TickerType`, `HistogramType`, `HistogramData`, and Java concurrency utilities.

## Risks and Test Signals
Tests should cover shutdown before statistics disposal, interruption, callback exceptions, empty input lists, interval timing, and exclusion of enum sentinels. A key risk is that callback thread safety is not guaranteed, and a thrown callback exception kills the collector task.
