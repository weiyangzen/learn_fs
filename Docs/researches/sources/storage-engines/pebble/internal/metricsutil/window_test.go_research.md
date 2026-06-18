<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/metricsutil/window_test.go -->
# sources/storage-engines/pebble/internal/metricsutil/window_test.go

Purpose: deterministic time test for `Window` using Go 1.25 `testing/synctest`.

Important APIs/functions: build-tagged `TestWindow` constructs `NewWindow[time.Duration]` with `startTime.Elapsed`, starts and stops it, advances fake time, and checks `TenMinutesAgo` and `OneHourAgo`.

Control flow and state: before ten minutes, `TenMinutesAgo` must return zero metric and zero timestamp. After roughly ten minutes, it expects the timestamp age to be around ten minutes and the sampled value near zero. After more time, it expects the ten-minute sample's metric to reflect about twenty minutes elapsed, and the one-hour sample to be between fifty and seventy minutes old with metric from the first ten minutes.

Dependencies and integration: depends on Go 1.25, `testing/synctest`, `time`, and `crtime`. It validates asynchronous timers without real sleeps. Risks not covered include repeated start/stop races, collect function panics, collection latency, and very long pauses. On older Go versions this test is excluded, so coverage depends on build environment.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/metricsutil/window_test.go -->
