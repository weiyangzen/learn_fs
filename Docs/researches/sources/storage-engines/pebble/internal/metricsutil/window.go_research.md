<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/metricsutil/window.go -->
# sources/storage-engines/pebble/internal/metricsutil/window.go

Purpose: generic sliding metrics window that periodically samples a caller-provided metric and returns approximate values from ten minutes and one hour ago.

Important APIs/types: `NewWindow[M]`, `CollectFn[M]`, `Window[M]`, `TenMinutesAgo`, `OneHourAgo`, `Start`, `Stop`, internal `tick`, constants `timeframeA`, `timeframeB`, `resolution`, `tickA`, `tickB`, and `ring[M]`.

Control flow and state: `Start` initializes rings and launches a goroutine to collect the initial sample without risking lock inversion with caller locks. It schedules a single timer at `tickA`; `tick` collects once, appends to the 10-minute and 1-hour rings as many times as required by elapsed time, then resets the timer to the next due sample. `Stop` marks the window stopped and stops the timer while holding the mutex.

Persistence and integration: state is in-memory; timestamps use monotonic `crtime.Mono`. The window is concurrency-safe around its mutex but `collectFn` is invoked under that mutex, so callers must avoid re-entering `Window` from collection. Risks include timer reset after very delayed ticks, zero values until rings wrap, generic metric copying cost, and no panic recovery around `collectFn`. Go 1.25 synctest coverage validates approximate behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/metricsutil/window.go -->
