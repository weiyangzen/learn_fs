# sources/test-tools/syzkaller/pkg/cover/file.go

Purpose: renders merged historical line coverage for a single source file as text or HTML and fetches merge results from BigQuery/GCS-backed coverage exports.

Important APIs/types/functions: `CoverageRenderConfig`, `DefaultTextRenderConfig`, `DefaultHTMLRenderConfig`, `RendFileCoverage`, `GetMergeResult`, `rendResult`, `RendTextLine`, `RendHTMLLine`, and `mainSignalSource`.

Control flow: `RendFileCoverage` fetches the requested file content through a `covermerger.FileVersProvider` and renders every line with the configured renderer. `GetMergeResult` builds a one-job `covermerger.Config`, exports namespace records for a time period, merges them, and returns the first channel result. Rendering optionally shows source explanation, hit count, line number, and escaped HTML.

State and persistence: no persistent state; external reads are file-provider, BigQuery export, and GCS reader operations. Rendering constructs strings in memory.

Dependencies and integration: bridges `pkg/cover`, `pkg/coveragedb`, and `pkg/covermerger`. It is likely used by coverage web handlers for per-file historical coverage.

Risks: `GetMergeResult` appears to return `nil, error` when `mr != nil` and `mr, nil` never happens, likely an inverted condition. The channel read uses a non-blocking `select` after `MergeCSVData`, so it assumes the single result is already buffered. `RendFileCoverage` does not handle a missing file version explicitly beyond empty map lookup.

Test signals: no direct tests in this subset. Integration coverage comes from `covermerger` and `coveragedb` tests, but this file's rendering and `GetMergeResult` branch deserve focused tests.
