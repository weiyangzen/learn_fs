# sources/test-tools/syzkaller/syz-cluster/dashboard/handler.go

## Purpose
Implements the web dashboard HTTP surface for syz-cluster. It renders series, sessions, tests, findings, builds, statistics, and raw artifacts/logs from Spanner-backed repositories and blob storage using embedded Go templates and embedded static assets.

## Important APIs, types, and functions
`dashboardHandler` is the central dependency container. It owns repositories for builds, series, sessions, session tests, test steps, findings, stats, and jobs, plus `blob.Storage` and parsed templates. `newHandler` wires the handler from `app.AppEnvironment`, parses `base.html`, common templates, and per-page templates. `Mux` registers all routes and serves embedded `/static/` assets. `seriesList`, `seriesInfo`, `sessionInfo`, and `statsPage` render HTML pages. `sessionLog`, `sessionTriageLog`, `sessionTestLog`, `sessionTestStepLog`, `sessionTestArtifacts`, `patchContent`, `jobPatchContent`, `allPatches`, `findingInfo`, and `buildInfo` expose raw blob-backed content. Helper functions include `getOffset`, `fetchSessionData`, `populateSeriesMetadata`, `groupFindings`, `makeMonthlyStats`, `renderTemplate`, `streamBlob`, and `errToStatus`.

## Control flow
Requests enter the `http.ServeMux`; route parameters are read with Go's `PathValue`. Page handlers query repositories, construct UI-specific structs, and call `renderTemplate`. `seriesList` builds a `db.SeriesFilter` from query parameters, applies a fixed page size of 100, and constructs prev/next URLs through `urlutil`. `seriesInfo` fetches the series, patches, versions, then all sessions and per-session test/finding/step metadata; job-backed sessions are collapsed by default and sessions are sorted to put non-job sessions first, then newest sessions. `sessionInfo` renders the same series template but for one session. `statsPage` collects weekly/monthly metrics from `StatsRepository` and computes totals. Raw content handlers resolve one database entity and stream the referenced blob URI to the response.

## State and persistence behavior
The file does not persist state directly. It reads all durable state from Cloud Spanner through `pkg/db` repositories and reads immutable or generated artifacts from configured `blob.Storage`. It also exposes a download content disposition for test artifact archives. Empty blob URIs are silently treated as empty responses, which is useful for optional artifacts but can hide missing data.

## Dependencies and integration points
Depends on `pkg/app` for environment/config, `pkg/db` for query contracts, `pkg/blob` for artifact reads, `pkg/service` for job links, and `pkg/html/urlutil` for query parameter rewriting. It integrates with dashboard templates under `dashboard/templates`, static assets under `dashboard/static`, Kubernetes service/deployment wiring, and API URL generation tested elsewhere through `pkg/api`.

## Risks and edge cases
Template execution writes directly to the response; if a template fails after partial output, `errToStatus` may append a 500 body after bytes have already been sent. `allPatches` concatenates patch blobs without separators beyond the stored bodies. `findingInfo` reads syz repro options and repro bodies fully into memory before writing. `getOffset` rejects negative and non-integer offsets, but page-next logic only checks whether the current page is full, not whether a next page exists. Raw blob handlers set limited content metadata, and most raw outputs rely on default content type.

## Test signals
Covered by `handler_test.go` for major generated URLs and all-patches concatenation, and by `local_ui_test.go` for manual browser-oriented data population. The tests exercise repository/blob integration using `app.TestEnvironment`, fake controller uploads, reporter-generated reports, and actual HTTP requests against an `httptest.Server`.
