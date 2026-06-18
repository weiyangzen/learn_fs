## sources/user-network-fs/gcsfuse/internal/workloadinsight/io_renderer.go

Purpose: Renders byte-range I/O access patterns as ASCII charts with file offset axes and summary statistics.

Important APIs/types/functions: constants `blockChar`, `emptyChar`, `labelHeader`; `Range`; `Renderer`; `NewRenderer`; `NewRendererWithSettings`; `Render`; helpers `humanReadable`, `buildStats`, `buildHeader`, `buildRow`, and `mapCoord`.

Control flow: renderer validates dimensions, builds header with name, stats, offset labels, and axis, then builds one row per range. Rows validate range ordering and file bounds, map start/end offsets to plot columns, mark covered columns with block characters, and truncate/pad labels.

State and persistence behavior: pure string rendering; no persistence.

Dependencies and integration points: intended for workload insight/debug output that visualizes file access distributions. Depends only on standard library formatting, math, sorting, and strings.

Risks: `buildRow` computes `e := rg.End - 1`, so zero-length ranges underflow and can produce misleading errors or plotting behavior. `mapCoord` treats zero file size as invalid, so rendering empty files with ranges fails. Unicode block character makes output non-ASCII.

Test signals: `io_renderer_test.go` covers constructor validation, human-readable formatting, coordinate mapping, golden outputs for several file sizes/range sets, and invalid render ranges.
