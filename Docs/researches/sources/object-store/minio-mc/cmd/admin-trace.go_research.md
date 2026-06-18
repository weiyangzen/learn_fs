# sources/object-store/minio-mc/cmd/admin-trace.go

## Purpose

`admin-trace.go` implements `mc admin trace`, a live and replayable trace viewer for MinIO service events. It supports trace-type selection, path/method/status/node/header/query/size/duration filters, concise and verbose output, JSON output, and statistical aggregation.

## Important APIs, Types, and Functions

`adminTraceFlags` declares the CLI filter and replay flags. `traceCallTypes` and `traceCallTypeAliases` map user call names into `madmin.ServiceTraceOpts`. `matchOpts.matches` applies local filtering. `tracingOpts` builds server-side trace options. `mainAdminTrace` orchestrates live service tracing or `--in` replay. Output types include `shortTraceMsg`, `traceMessage`, `requestInfo`, `responseInfo`, `callStats`, `verboseTrace`, `statItem`, and `statTrace`.

## Control Flow

The handler validates arity and incompatible flags, configures colors, creates a cancellable context, then chooses input mode. In replay mode it reads newline-delimited JSON, optionally through zstd, decodes short trace records, skips bootstrap records, and sends reconstructed `ServiceTraceInfo` values through a buffered channel. In live mode it creates an admin client, builds trace options, and consumes `client.ServiceTrace`. If `--stats` or replay is active, traces are filtered and sent to a Bubble Tea stats UI. Otherwise each matching trace is printed as verbose or short output.

## State and Persistence Behavior

Live mode does not persist trace data. Replay mode reads a saved JSON or `.zst` file but does not write it. Runtime aggregation is held in `statTrace` with a mutex, tracking per-function counts, durations, errors, byte totals, TTFB, and time bounds.

## Dependencies and Integration Points

The file is tightly integrated with `madmin-go` trace types, `newAdminClient`, `globalContext`, MinIO path/name/pattern matching helpers, `humanize.ParseBytes`, `zstd`, Bubble Tea stats UI hooks, color JSON, and shared message printing. It depends on server-side trace option support for selected call families.

## Risks and Edge Cases

`shortTrace` assumes HTTP details exist for S3/internal traces; malformed server data could panic. Replay reconstruction loses HTTP request/response details and uses an unexported `trcType` field that cannot be recovered from JSON, so stats from saved short JSON are less complete. Header and query filters support negation with `!`, but matching semantics are local and pattern-based. The replay goroutine closes the channel then blocks forever with `select {}`, relying on process exit. Verbose string rendering mutates request headers by deleting `Host`.

## Test Signals

Good tests should cover syntax validation, `--all` versus `--call`, trace call alias mapping, size parsing, positive and negated header/query filters, path/name matching, JSON encoding with HTML escaping disabled, non-HTTP trace formatting, stats aggregation, and replay of plain and zstd trace files.
