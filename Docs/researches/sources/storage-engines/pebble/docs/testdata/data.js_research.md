# sources/storage-engines/pebble/docs/testdata/data.js

## Purpose

This local fixture defines a global `data` object for `local-test.html`. It mirrors the remote Pebble benchmark `data.js` shape with synthetic YCSB benchmark series so the docs UI can be exercised without loading the S3-hosted fixture.

Each property is a workload key and each value is a newline-delimited CSV string. `app.js` parses these strings into arrays of benchmark datapoints during `initData()`.

## Important Data Shape

The file assigns `data = { ... }` without `var`, `let`, or `const`, intentionally creating or replacing a browser-global `data` binding for the legacy script stack.

It contains 12 workload keys:

- `ycsb/A/values=1024`
- `ycsb/A/values=64`
- `ycsb/B/values=1024`
- `ycsb/B/values=64`
- `ycsb/C/values=1024`
- `ycsb/C/values=64`
- `ycsb/D/values=1024`
- `ycsb/D/values=64`
- `ycsb/E/values=1024`
- `ycsb/E/values=64`
- `ycsb/F/values=1024`
- `ycsb/F/values=64`

Each workload has 10 CSV rows spanning dates from January 25, 2026 through February 3, 2026. Rows use the schema consumed by `app.js`:

1. Date string, either `YYYYMMDD` or `YYYYMMDD-sha`.
2. `opsSec`.
3. `readBytes`.
4. `writeBytes`.
5. `readAmp`.
6. `writeAmp`.

The fixture intentionally includes both date-only rows and date-with-SHA rows. That exercises `parseDateStr`, which strips the SHA suffix for date parsing and stores the suffix separately.

## Control Flow

There are no functions. The file executes a single top-level assignment when loaded by the browser. The later `app.js` initialization flow reads the global `data`, parses each CSV string with `d3.csvParseRows`, computes global and per-chart maxima, then fetches write-throughput summary data and merges it into the same `data` object.

`local-test.html` loads this file before `write-throughput.js` and `app.js`, so by the time `window.onload` runs, the YCSB fixture is available.

## State and Persistence Behavior

The file seeds mutable in-memory global state only. It does not persist data to storage or make network requests. `app.js` mutates the global `data` object by replacing each CSV string with parsed arrays and adding write-throughput arrays fetched from local or remote summary JSON.

Because the assignment is unqualified, any previous global `data` value is overwritten when this script loads.

## Dependencies

This fixture has no code dependencies. It depends structurally on `app.js` expecting a global object of CSV strings. It is integrated through `local-test.html`, not through an import system.

The data is coupled to:

- `app.js` CSV parsing and date parsing.
- `app.js` chart rendering for YCSB workloads.
- `write-throughput.js` indirectly, because `app.js` merges write-throughput summary data into this same object before calling the write-throughput renderer.

## Integration Points

`local-test.html` loads:

1. `js/d3.v5.min.js`
2. `testdata/data.js`
3. `js/write-throughput.js`
4. `js/app.js`

That means this fixture is the local replacement for the remote `https://pebble-benchmarks.s3.amazonaws.com/data.js` script used by `index.html`.

The workload keys are expected by the YCSB chart sections in the docs UI. The write-throughput chart does not consume these YCSB keys directly, but shares the global `data` object after `initData()` merges write-throughput summary rows.

## Risks

- The global assignment lacks a declaration and will fail under strict mode or module loading. This is acceptable for the current legacy script style but fragile for modernization.
- Because values are raw CSV strings, schema changes in `app.js` can silently misparse fixtures if the column order is changed.
- The fixture contains synthetic-looking future dates and mixed SHA formats. That is useful for parser coverage but may not reflect production freshness semantics.
- Missing or malformed rows in a single workload could break chart rendering because parsing and max computation assume numeric columns.
- The local fixture does not include write-throughput summary data; that lives in `testdata/write-throughput/summary.json` and is fetched separately.

## Test Signals

Useful checks:

- Evaluate the script and confirm `Object.keys(data).length === 12`.
- Confirm every workload has 10 newline-delimited rows and every row has six comma-separated fields.
- Confirm rows with and without SHA suffixes both parse through `parseDateStr`.
- Load `local-test.html` and verify YCSB charts render without using the remote S3 `data.js`.
- Verify that after `app.js` initialization, each workload value has been converted from a CSV string into parsed row objects with numeric metric fields.
