<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/trace-stats-ui.go -->
# sources/object-store/minio-mc/cmd/trace-stats-ui.go

Purpose: implements the terminal statistics UI for service trace events, used by `support top api` and related trace summaries.

Important APIs/types/functions: `traceStatsUI`, `Update`, `View`, `ibytesShort`, `roundDur`, and `initTraceStatsUI`.

Control flow: initialization creates a spinner, configures console colors, constructs a `statTrace`, and starts a goroutine that adds incoming `madmin.ServiceTraceInfo` values to the stats accumulator. `Update` handles quit, reset min/max (`r`), and scrolling keys. `View` reads accumulated calls under lock, computes duration, RX/TX rates, total RPM, sorts calls by count, applies viewport truncation based on `maxEntries` and offset, optionally includes TTFB columns, colors durations by thresholds, and truncates rendered lines to terminal width.

State and persistence: in-memory aggregate stats only. Reset mutates current min/max fields but does not clear counts.

Dependencies and integration points: depends on `statTrace`/`statItem` types from trace code, Bubble Tea, spinner, tablewriter, terminal width detection, console color registry, and humanized byte formatting.

Risks and test signals: duration can be zero early in collection, which can affect rate calculations. Tests should cover empty state, reset behavior, TTFB column appearance, truncation/offset boundaries, duration color thresholds, and concurrent add/render locking.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/trace-stats-ui.go -->
