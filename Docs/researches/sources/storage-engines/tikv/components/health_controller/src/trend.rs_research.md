# sources/storage-engines/tikv/components/health_controller/src/trend.rs

Purpose: rolling-window trend detector for slow-cause latency and slow-result QPS changes.

Important APIs/types/functions: `SampleWindow`, `SampleWindows`, `HistoryWindow`, `SpikeFilter`, `Trend`, `CurvesComposer`, and `RequestPerSecRecorder`.

Control flow: `Trend::record` samples according to interval, optionally spike-filters once history is established, records into L0/L1/L2 windows, updates history baselines, and exposes composed increasing rate from L0/L1 and L1/L2 comparisons after margins are subtracted. History windows flip to new baselines after sustained large shifts stabilize.

State and persistence: in-memory `VecDeque` sample windows, overflow flags, timestamps, history windows, and Prometheus gauges.

Dependencies/integration: used by `SlowTrendStatistics` to publish `SlowTrend` cause/result values; depends on Prometheus and TiKV logging.

Risks: heuristic constants strongly influence sensitivity; spike filter is currently disabled by reporter config; time-based flipping behavior is subtle.

Test signals: direct test covers sample-window average, standard deviation, validity, and overflow.
