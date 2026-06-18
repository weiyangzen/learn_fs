# sources/test-tools/syzkaller/dashboard/app/public_json_api.go

## Purpose

`public_json_api.go` converts dashboard UI page models into stable public JSON API descriptions and streams coverage data in an external coverage format. It is the bridge between template-oriented structs in `main.go` and `github.com/google/syzkaller/dashboard/api` consumers.

## Important APIs, Types, and Functions

`getExtAPIDescrForBug` maps `uiBugDetails` to `api.Bug`, including title, ID, status, crash times, optional fix/close times, discussions, fix commits, cause bisection commit, and crash descriptors. `getBugFixCommits` maps `uiCommit` to `api.Commit` and preserves optional dates. `getExtAPIDescrForBugGroups` flattens `uiBugGroup` lists into `api.BugSummary` records. Backport JSON uses local structs `publicKernelTree`, `publicBackportBug`, `publicMissingBackport`, and `publicAPIBackports` plus `getExtAPIDescrForBackports`.

`GetJSONDescrFor` is the central dispatcher. It accepts `*uiBugPage`, `*uiTerminalPage`, `*uiMainPage`, `*uiBackportsPage`, and selected dungeon/AI page types, returning indented JSON or `ErrClientNotFound`. Coverage export is handled by `writeExtAPICoverageFor`, `writeFileCoverage`, and `genFuncsCov`.

## Control Flow

For page JSON, handlers in `main.go` build the normal UI page model, then call `GetJSONDescrFor`. That function selects a conversion path and marshals with `json.MarshalIndent`. For coverage JSON, `writeExtAPICoverageFor` chooses the previous completed month, builds a `coveragedb.FunctionFinder`, streams file coverage rows for namespace/subsystem/manager scope, and delegates each file to `writeFileCoverage`. `writeFileCoverage` turns each file row into a `cover.FileCoverage` JSON object and writes one encoded object per stream item. `genFuncsCov` groups line hit counts by function name using `FunctionFinder.FileLineToFuncName`.

## State and Persistence Behavior

This file does not write persistent application state. It reads already-sanitized UI models and coverage DB data. Coverage output depends on current wall-clock month via `time.Now`, not `timeNow(ctx)`, so tests need fixture control through the coverage DB mock rather than dashboard fake time.

## Dependencies and Integration Points

It depends on `dashboard/api`, `pkg/cover`, `pkg/coveragedb`, civil dates, and the UI structs from `main.go`. Its consumers are page handlers that support `?json=1` and external API clients. Coverage streaming integrates with the coverage database client stored in context.

## Risks and Edge Cases

Because JSON is derived from UI structs, access filtering must happen before conversion; this file assumes the page model is already safe. `getExtAPIDescrForBackports` assumes each backport bug has crash data when JSON is requested by `handleBackports(loadCrashes=true)`. `writeFileCoverage` exits silently on context cancellation, which avoids noisy failures but can produce partial output. `genFuncsCov` assumes `HitCounts` and `LinesInstrumented` are aligned arrays; mismatch would panic through indexing. Map iteration over function names is not sorted, so function ordering can be unstable unless upstream data or tests constrain it.

## Test Signals

`public_json_api_test.go` covers bug page JSON, bug-group JSON, fix commit metadata, cause bisection JSON, API client integration, and coverage export formatting with mocked coverage DB rows.
