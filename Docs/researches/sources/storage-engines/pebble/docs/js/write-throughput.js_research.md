# sources/storage-engines/pebble/docs/js/write-throughput.js

## Purpose

This browser-global script renders the Pebble write-throughput benchmark charts in the docs UI. It fetches a summary JSON file, renders a time-series chart for the `write/values=1024` workload, supports hover/zoom/click interactions, fetches per-run detail JSON for the selected date, parses worker-level CSV data, and renders the detail chart.

The file is part of a non-module script stack. It defines globals used by `app.js`, and it also depends on globals supplied by `app.js`, which is called out by a TODO in `app.js` as an awkward script-loading relationship.

## Important APIs, Types, and Functions

- `writeThroughputWorkload`: global constant with value `write/values=1024`. `app.js` uses it to pick the default workload for initial detail rendering.
- `isLocalMode()`: reads `window.location.search` through `URLSearchParams` and returns true only when `local=true`.
- `writeThroughputSummaryURL()`: returns `testdata/write-throughput/summary.json` in local mode, otherwise `https://pebble-benchmarks.s3.amazonaws.com/write-throughput/summary.json`.
- `writeThroughputDetailURL(filename)`: returns a local or S3 detail URL under the same `write-throughput` prefix.
- `bisectAndRenderWriteThroughputDetail(data, detailDate)`: uses a D3 bisector on parsed dates to select a summary datapoint, fetches its detail data, then renders the detail chart. Fetch failures render the detail chart with `null` data.
- `renderWriteThroughputSummary(allData)`: renders the summary time series, axes, clip path, hover labels, marker, synchronized zoom callback, synchronized mouse callback, and click handler.
- `fetchWriteThroughputSummaryData(file)`: fetches a detail JSON file and converts each run's `rawData` CSV string into numeric row objects `{ elapsed, opsSec, passed, size, levels }`.
- `renderWriteThroughputSummaryDetail(workload, date, opsSec, rawData)`: clears and redraws the detail chart for worker-level ops/sec over elapsed time, with a dashed average line at the calculated `opsSec`.

The expected summary data shape is an object keyed by workload name, with arrays of objects containing `name`, `date`, `opsSec`, optional `sha`, `writeAmp`, and `summaryPath`. The expected detail data shape is an object keyed by worker/run id, where each value contains `rawData` CSV rows before parsing and `data` row objects after parsing.

## Control Flow

The main flow is orchestrated by `app.js`, not by this file directly:

1. `app.js` calls `initData()`, which fetches `writeThroughputSummaryURL()` and merges each returned workload into the global `data` object.
2. `app.js` calls `renderWriteThroughputSummary(data)` after initializing date range, annotations, and query params.
3. `renderWriteThroughputSummary` selects `.chart.write-throughput`, picks `allData["write/values=1024"]`, computes dimensions from `styleWidth` and `styleHeight`, creates time/linear scales, renders axes and a single SVG line, then attaches hover and zoom state to the SVG DOM node.
4. The summary chart installs a transparent mouse rectangle. Mouse movement updates all charts with an `updateMouse` method, mouse over/out toggles hover opacity, and click floors the x-coordinate date to a day and calls `bisectAndRenderWriteThroughputDetail`.
5. On initialization, `app.js` also calls `bisectAndRenderWriteThroughputDetail(data[writeThroughputWorkload], max.date)` so the detail chart is populated for the latest selected date.
6. The detail fetch path calls `fetchWriteThroughputSummaryData(summaryPath)` and then `renderWriteThroughputSummaryDetail`. If the fetch rejects, the detail chart receives `rawData = null` and displays "Data unavailable".

The zoom callback updates the summary chart locally for programmatic zoom events, and broadcasts user-originated zoom transforms to every `.chart` node with an `updateZoom` method. It then normalizes each chart node's `__zoom` transform by forcing the y translation to zero.

## State and Persistence Behavior

This script does not use persistent browser storage. Runtime state lives in:

- DOM nodes and SVG children appended under `.chart.write-throughput` and `.chart.write-throughput-detail`.
- `svg.node().updateMouse` and `svg.node().updateZoom` callback properties.
- D3 zoom state on SVG nodes, including `__zoom`.
- Hover SVG elements whose opacity and text are updated on mouse events.

The detail chart is explicitly cleared with `svg.selectAll("*").remove()` before each render to avoid accumulating old runs. The summary chart is not cleared by this function, so repeated calls to `renderWriteThroughputSummary` would append duplicate axes, paths, clip paths, mouse rectangles, and handlers.

The local/remote mode is derived from the current URL query string on each URL helper call. No query state is mutated by this file.

## Dependencies

Direct browser/runtime dependencies:

- Global `d3` from `d3.v5.min.js`.
- Browser `fetch`.
- Browser `URLSearchParams`.
- DOM/SVG APIs through D3 selections.
- `window.location.search`.

Project-global dependencies supplied by `app.js`:

- `parseTime`
- `formatTime`
- `styleWidth`
- `styleHeight`
- `minDate`
- `max.date`

Data dependencies:

- Remote summary and detail JSON under `https://pebble-benchmarks.s3.amazonaws.com/write-throughput/`.
- Local summary fixture at `testdata/write-throughput/summary.json` when `?local=true`.
- Local detail fixture files matching each `summaryPath`, if present, for click-through detail testing.

## Integration Points

The HTML pages include two relevant SVGs:

- `.chart.write-throughput`
- `.chart.write-throughput-detail`

`index.html` loads D3, remote `data.js`, `write-throughput.js`, and then `app.js`. `local-test.html` loads D3, local `testdata/data.js`, `write-throughput.js`, and then `app.js`.

`app.js` consumes this file by calling `writeThroughputSummaryURL`, `renderWriteThroughputSummary`, `bisectAndRenderWriteThroughputDetail`, and reading `writeThroughputWorkload`. In the other direction, this file calls helpers that are defined later by `app.js`. That works because those helper-dependent functions are not invoked until `window.onload`, after all scripts have been evaluated.

## Risks

- `bisectAndRenderWriteThroughputDetail` does not guard against the bisector returning `data.length`; unlike the hover code, it immediately reads `data[i]`. A click or initial date beyond the last datapoint may throw when accessing `workload.date`.
- `renderWriteThroughputSummaryDetail` iterates `for (let key in rawData)` before checking `rawData == null`. The intended "Data unavailable" branch is unreachable for `null` and will throw before rendering the fallback.
- `const noData = mousex < x(parseTime(data[0].date));` is computed but unused, and the hover logic still indexes `data[i - 1]` when the mouse is before the first datapoint. With `i === 0`, this can read `data[-1]` and throw.
- `renderWriteThroughputSummary` hardcodes `dataKey = "write/values=1024"` even though the SVG has `data-key` and the file defines `writeThroughputWorkload`. This limits reuse and can drift from markup/configuration.
- The clip path id is set to `write/values=1024`, which contains slash and equals characters. It works in many SVG URL contexts but is brittle for CSS selectors and duplicate chart instances.
- The script relies on D3 v5 globals such as `d3.event` and `d3.mouse`, which are migration hazards for newer D3.
- There is no explicit handling for missing workload keys, empty data arrays, malformed dates, non-OK fetch responses, or malformed detail `rawData`.

## Test Signals

High-value test cases:

- Load `local-test.html?local=true` and confirm the summary fetch uses `testdata/write-throughput/summary.json`.
- Load the normal page and confirm the summary fetch uses the S3 URL.
- Render the summary chart from a fixture with 10 ordered datapoints and verify an SVG path, x/y axes, hover marker, and mouse interaction rectangle are created.
- Hover before the first point, between points, and after the last point to exercise bisector boundary behavior.
- Click on a valid date and confirm `fetchWriteThroughputSummaryData` parses detail `rawData` into numeric `{ elapsed, opsSec, passed, size, levels }` rows.
- Simulate detail fetch failure and verify whether the fallback "Data unavailable" path works; current code appears to throw before reaching the null check.
- Zoom the summary chart and verify x-axis/path updates and that other chart nodes with `updateZoom` receive synchronized transforms.
