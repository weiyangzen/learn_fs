# sources/storage-engines/foundationdb/contrib/replay/trace.go

## Purpose

`trace.go` parses FoundationDB XML trace files into indexed in-memory data for the replay TUI. It stores every trace event, extracts database configuration snapshots, recovery states, epoch/version relationships, and provides binary-search helpers for time and event-index navigation.

## Important APIs, Types, and Functions

- `TraceEvent` stores common XML event attributes (`Severity`, `Time`, `DateTime`, `Type`, `Machine`, `ID`), parsed `TimeValue`, and all other attributes in `Attrs`.
- `DBConfig` captures selected fields from the HTML-encoded JSON `Conf` attribute on `MasterRecoveryState` events, plus `RawJSON`.
- `RecoveryState` records time, status code, status text, and the event index of a `MasterRecoveryState`.
- `EpochVersionInfo` correlates recovery epoch data with known committed/recovery versions from `GetDurableResult` and `UpdateRegistration`.
- `TraceData` stores sorted slices of events, configs, recovery states, epoch version info, min/max time, and a default scrub `TimeStep`.
- `parseTraceFile(filepath string)` streams XML, builds slices, sorts them, builds indices, and returns `TraceData`.
- `parseDBConfig(confStr string, time float64)` decodes HTML entities, parses JSON, and extracts common config fields.
- Query helpers:
  - `GetEventsUpToTime(targetTime float64)`
  - `GetLatestConfigAtTime(targetTime float64)`
  - `GetLatestRecoveryStateAtIndex(eventIndex int)`
  - `GetLatestEpochVersionAtIndex(eventIndex int)`
  - `FindPreviousRecovery(eventIndex int)`
  - `FindNextRecovery(eventIndex int)`
  - `FindPreviousRecoveryWithStatusCode(eventIndex int, statusCode string)`
  - `FindNextRecoveryWithStatusCode(eventIndex int, statusCode string)`
  - `GetEventIndexAtTime(targetTime float64)`

## Control Flow

`parseTraceFile()` opens the file, estimates event capacity from file size, creates an `xml.Decoder`, and loops through XML tokens. For each `<Event>` start element, it builds a `TraceEvent`, mapping known attributes to top-level fields and storing all other attributes in `Attrs`. `Time` is parsed as float and updates `maxTime`. Every event is appended.

While streaming, `MasterRecoveryState` events with a `Conf` attribute are passed to `parseDBConfig()` and appended to `configs` if JSON parsing succeeds.

After EOF, the function sorts events and configs by time. It then builds:

- `RecoveryStates` by scanning sorted events for `MasterRecoveryState` events with both `StatusCode` and `Status`, storing the sorted event index.
- `EpochVersions` with two passes: first collect KCV by recovery/end version from `GetDurableResult`, then scan `UpdateRegistration` events for epoch, recovery transaction version, and last epoch end. Valid entries are optionally enriched with KCV when the last epoch end matches a collected durable result.
- `TimeStep` by sampling up to the first 10,000 sorted events and selecting the smallest positive interval, with `0.1` fallback.

The query helpers rely on sorted slices and `sort.Search`. Time-based helpers search on `TimeValue` or config `Time`; recovery/epoch helpers search on `EventIndex`.

## State and Persistence Behavior

All parsed data is held in memory. `TraceEvent.Attrs` maps own string copies produced by the XML decoder. There is no on-disk cache or incremental persistence. `GetEventsUpToTime()` returns a slice view of `td.Events`, not a copy; callers should treat it as read-only.

`MinTime` is initialized to `0.0` and never updated during parsing. For traces whose first event time is not zero or whose events all have positive times, `MinTime` will still be zero. `MaxTime` is updated while streaming before sorting.

The parser prints progress and status to stdout, while `main.go` prints its summary to stderr. This mixed output is acceptable for an interactive tool but relevant for scripts/tests.

## Dependencies and Integration Points

This file uses standard packages `encoding/xml`, `encoding/json`, `fmt`, `html`, `io`, `os`, `sort`, and `strconv`. It is consumed by `main.go` for initial load, by `cluster.go` through `TraceEvent`, and by `ui.go` for navigation, configuration display, recovery status display, and epoch/version panels.

## Risks and Edge Cases

- The entire trace is stored in memory. Very large XML traces can consume substantial RAM despite streaming token decoding.
- `MinTime` is not computed, so UI ranges or summaries using it may be misleading.
- XML decoder errors abort the whole load; malformed late events lose all earlier parsed data.
- `file.Stat()` ignores its error before calling `fileInfo.Size()`, though stat on an open file normally succeeds. If it failed, this would panic.
- Config JSON parsing silently drops malformed configs by returning nil.
- Numeric config fields are decoded as `float64` and converted to `int`; large values or non-integer JSON numbers could truncate.
- `strconv.ParseInt` errors for version fields are ignored, turning malformed values into zero and potentially filtering or mis-correlating epoch data.
- `kcvByRV` stores one KCV per end version; duplicate `GetDurableResult` events for the same end version overwrite prior entries.
- `GetEventIndexAtTime()` returns `len(td.Events)-1` when target is after the last event, but if `td.Events` is empty this returns `-1`. Callers must handle empty traces.
- Query helpers return pointers into slices. Those remain stable while slices are not reallocated, but callers should not append to the stored slices concurrently.
- Sorting solely by `TimeValue` is not stable. Same-time event ordering may change, which can matter for role transitions or recovery state indexing.

## Test Signals

Tests should parse minimal and multi-event trace XML, malformed XML, events with extra attributes, missing/invalid time values, `MasterRecoveryState` configs with HTML-encoded JSON, malformed config JSON, recovery states with and without status fields, durable/update epoch matching, duplicate same-time events, empty traces, and query boundaries before first event, exactly on an event, between events, and after the last event.

Performance tests should exercise large traces to observe memory growth, progress logging, sort time, and query latency. Integration tests should validate `BuildClusterState()` and `ui.go` consumers against sorted event slices with event-index semantics.
