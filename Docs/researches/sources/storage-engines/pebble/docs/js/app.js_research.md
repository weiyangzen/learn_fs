# sources/storage-engines/pebble/docs/js/app.js

## Purpose
`docs/js/app.js` implements the client-side D3 application used by Pebble's benchmark dashboard. It parses benchmark data, renders YCSB time-series charts, supports global or per-chart maxima, overlays optional detail series, synchronizes zoom and hover state across charts, displays annotations and commit SHA hints, loads write-throughput summary data, and persists selected chart options in query parameters.

## Important APIs, types, and functions
Date helpers include `parseDateStr`, which accepts `YYYYMMDD` or `YYYYMMDD-sha`, and `parseTime`, which returns only the date. Formatting and geometry helpers include `formatTime`, `dateBisector`, `styleWidth`, `styleHeight`, `pathGetY`, `humanize`, `dirname`, and `equalDay`.

Data shaping functions include `computeSegments`, which splits a series into contiguous daily runs, and `computeGaps`, which creates dashed gap segments between non-contiguous runs and from the last datum to the dashboard max date. `initData` parses the global `data` object's CSV rows into objects with date, sha, ops/sec, read/write bytes, and read/write amplification, computes global and per-chart maxima, then fetches `writeThroughputSummaryURL()` and merges summary records. `initDateRange`, `initAnnotations`, `initQueryParams`, `setQueryParams`, `setDetail`, `toggleDetail`, and `toggleLocalMax` initialize or update UI state.

`renderChart` is the main renderer. It clears an SVG chart, computes dimensions and scales, draws axes, handles no-data charts, creates clip paths, renders annotations, splits and draws solid and dashed line segments, optionally renders a second detail axis and line, installs synchronized D3 zoom behavior, and creates hover overlays for date, value, marker, and short SHA. `renderYCSB` applies `renderChart` to every `.chart.ycsb` element. `window.onload`, `window.onpopstate`, and the resize listener bootstrap and refresh the dashboard.

## Control flow, state, and persistence
The script uses module-level mutable state: `minDate`, `max`, `usePerChartMax`, `detail`, `detailName`, `detailFormat`, and `annotations`. On page load, it wires toggle links, loads and parses data, initializes date range and annotations, restores query params, renders YCSB charts and write-throughput panels, sets the "last updated" text, and then toggles local-max mode by default.

Charts share zoom state by broadcasting the active D3 transform to all `.chart` nodes with an `updateZoom` function. Hover state is similarly broadcast with `updateMouse`, causing all charts to show the closest datapoint for the same date. The detail series is selected globally through query parameters and can be read bytes, write bytes, read amplification, or write amplification. Annotations are read from DOM nodes with class `.annotation` and rendered as green markers/vertical lines; hovering near an annotation temporarily replaces the chart title with the annotation message.

## Dependencies and integration points
The file assumes D3 is globally available and uses D3 v5-era APIs such as `d3.event` and `d3.mouse`. It assumes global variables and functions from surrounding documentation scripts: `data`, `writeThroughputSummaryURL`, `renderWriteThroughputSummary`, `writeThroughputWorkload`, and `bisectAndRenderWriteThroughputDetail`. HTML integration depends on `.chart.ycsb` SVG elements, `.toggle` controls, `#localMax`, `.annotation` elements with `data-date`, and `.updated` targets.

## Risks and invariants
Several functions assume non-empty data arrays. `computeGaps` indexes the last segment and will fail if a chart has an empty series. `dirname` assumes a slash exists in the path. `initData` uses `for (key in data)` without declaring `key`, creating or reusing a global. The write-throughput merge path replaces parsed dates with `d.date.split("-")[0]`, a string, while the charting logic expects `Date` objects; this is safe only if downstream write-throughput functions do not feed those records back into YCSB chart paths that require dates. `pathGetY` operates on the first rendered path node for a series, so hover-series selection can be inaccurate when data is split into multiple segments. Query parameter updates push history entries for each toggle. The script is tied to older D3 event APIs and would need changes for D3 v6+.

## Test signals
There are no local tests for this JavaScript file in the researched set. Practical validation would require loading the docs page with representative `data`, annotations, and write-throughput summary responses, then checking rendering, zoom synchronization, hover values, detail toggles, query params, resize behavior, empty-chart behavior, and SHA display.
