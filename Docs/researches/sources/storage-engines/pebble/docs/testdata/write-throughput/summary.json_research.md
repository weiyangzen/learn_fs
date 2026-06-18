# sources/storage-engines/pebble/docs/testdata/write-throughput/summary.json

## Purpose

This JSON fixture supplies local write-throughput summary data for the Pebble docs UI. It is used when `writeThroughputSummaryURL()` sees `?local=true`, allowing `local-test.html` or the normal docs page in local mode to render the write-throughput summary chart without fetching the S3 summary.

## Important Data Shape

The top-level object has one workload key:

- `write/values=1024`

The value is an array of 10 summary datapoints. Each object contains:

- `name`: workload name, always `write/values=1024` in this fixture.
- `date`: benchmark date, usually `YYYYMMDD-sha`; one row uses date only (`20260129`).
- `opsSec`: calculated max sustainable write throughput.
- `writeAmp`: write amplification metric for the run.
- `summaryPath`: detail JSON filename for per-worker time-series data.

The fixture spans January 25, 2026 through February 3, 2026. `opsSec` ranges from 58,825 to 68,000 in the provided rows. `summaryPath` values follow the pattern `YYYYMMDD-pebble-write-size=1024-run_1-summary.json`.

## Control Flow

This file is data-only. It is fetched by `writeThroughputSummaryURL()` through the `initData()` flow in `app.js`:

1. `app.js` calls `fetch(writeThroughputSummaryURL())`.
2. The response JSON is parsed.
3. For each workload key, `app.js` maps each datapoint to a new object that preserves the original fields, rewrites `date` to the date-only prefix, and stores the parsed SHA suffix in `sha`.
4. The resulting array is assigned into the global `data` object under `write/values=1024`.
5. `renderWriteThroughputSummary(data)` reads this array and draws the summary chart.
6. Clicks or initial detail rendering use `summaryPath` to fetch a corresponding detail file through `writeThroughputDetailURL()`.

## State and Persistence Behavior

The fixture is static JSON and has no internal state. Once fetched, its values become mutable in-memory objects owned by `app.js` and `write-throughput.js`.

No persistence occurs. The `summaryPath` fields are references to additional detail fixtures or remote detail files; this file does not embed the worker-level `rawData` used by the detail chart.

## Dependencies

The file depends on the schema expected by `app.js` and `write-throughput.js`. The chart code expects:

- A top-level key matching `writeThroughputWorkload` / `write/values=1024`.
- A non-empty, date-sorted array.
- Valid `date` strings parseable by `parseDateStr`.
- Numeric `opsSec`.
- Valid `summaryPath` values for detail fetches.

It is selected by `writeThroughputSummaryURL()` when local mode is enabled.

## Integration Points

Local mode URL resolution points to `testdata/write-throughput/summary.json`. The HTML pages provide the SVG containers, `app.js` performs the fetch/merge, and `write-throughput.js` renders the resulting series.

Each `summaryPath` integrates with `fetchWriteThroughputSummaryData`, which expects the corresponding detail JSON file to be located under `testdata/write-throughput/` in local mode or the S3 `write-throughput/` prefix in remote mode.

## Risks

- The chart assumes sorted data for bisector behavior. If rows are reordered, hover and click selection can become incorrect.
- One fixture row lacks a SHA suffix. That is useful for parser coverage, but any UI logic assuming `sha` exists must handle null.
- Missing local detail files for `summaryPath` entries cause the detail fetch to reject. The intended fallback currently has a bug in `renderWriteThroughputSummaryDetail` because it iterates `rawData` before checking for null.
- The summary contains `writeAmp`, but `renderWriteThroughputSummary` only plots `opsSec`; if future charting expects write amplification, code changes are needed.
- Date values are future-dated relative to many real benchmark histories; freshness indicators in `app.js` will reflect the fixture dates rather than current production data.

## Test Signals

Useful validation:

- JSON parses successfully and has exactly one top-level key, `write/values=1024`.
- The array has 10 entries sorted by date from `20260125` to `20260203`.
- Every entry has `name`, `date`, numeric `opsSec`, numeric `writeAmp`, and `summaryPath`.
- At least one date with SHA and one date without SHA parse through `parseDateStr`.
- In local mode, `app.js` merges this array into global `data` and `renderWriteThroughputSummary` draws the summary line.
- Clicking a datapoint should attempt to fetch the matching `summaryPath` under `testdata/write-throughput/`.
