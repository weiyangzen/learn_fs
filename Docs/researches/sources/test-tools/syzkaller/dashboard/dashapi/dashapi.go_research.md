# sources/test-tools/syzkaller/dashboard/dashapi/dashapi.go Research

## Purpose
Package `dashapi` defines the wire data model and HTTP client used by syzkaller components to communicate with the dashboard. It covers build upload, builder polling, jobs, crashes, repros, reporting, bug lists, discussions, coverage, manager stats, assets, bug loading, email sending, and shared recipient/status enums.

## Important APIs and types
- Client construction: `Dashboard`, `DashboardOpts`, `UserAgent`, `New`, `NewCustom`, `RequestCtor`, `RequestDoer`, and `RequestLogger`. Empty API keys trigger ambient GCE bearer-token auth through `pkg/auth`.
- Build/commit flow: `Build`, `Commit`, `UploadBuild`, `BuilderPoll`, `CommitPoll`, and `UploadCommits`.
- Job flow: `JobResetReq`, `JobPollReq`, `ManagerJobs.Any`, `JobPollResp`, `JobDoneReq`, `JobType`, `JobDoneFlags.String`, `JobPoll`, `JobDone`, and `JobReset`.
- Crash/repro flow: `Crash`, `ReportCrash`, `CrashID`, `NeedRepro`, `ReportFailedRepro`, `LogToRepro`, and `ReproTaskDone`.
- Reporting model: `BugReport`, `ReportElements`, `BugSubsystem`, `Asset`, `BisectResult`, `BugListReport`, `BugUpdate`, `BugNotification`, discussion structs, `TestPatchRequest`, manager stats, assets, bug loaders, and email request types.
- Transport core: `Dashboard.Query` and `queryImpl`.

## Control flow
Most exported methods build a request struct, call `Query` with a dashboard method string, and return the decoded response. `Query` logs requests/replies when configured, calls `queryImpl`, invokes an error handler on failure, and retries failed API calls up to three times with one-second sleeps. `queryImpl` zeroes non-nil reply pointers, constructs a multipart POST to `<Addr>/api`, writes `client`, `key`, `method`, and gzipped JSON `payload`, sends it through the configured doer, checks for HTTP 200, and JSON-decodes the response body into `reply`.

## State and persistence
The client stores only endpoint, key, injected constructor/doer/logger/error handler, and optionally an auth token cache hidden in the wrapped doer. Persistent dashboard state is remote: builds, bugs, crashes, jobs, reports, assets, discussions, coverage, and emails. `queryImpl` intentionally resets reply values before decoding to avoid stale fields after partial JSON updates.

## Dependencies and integration points
Depends on Go standard packages for HTTP, multipart, gzip, JSON, reflection, mail addresses, and timing, plus `github.com/google/syzkaller/pkg/auth`. The structs are compatibility contracts with dashboard server handlers and syz-ci/reporting clients; comments warn that asset type strings must not change because DB content depends on them.

## Risks
The transport retries all errors, which can duplicate side effects if the server performed an action but returned an error or the response was lost. Requests have no explicit context/timeout at this layer. Reflection requires `reply` to be a pointer and only catches misuse at runtime. Multipart/gzip JSON is a custom protocol that must stay in lockstep with the server. Some fields are deprecated but retained for compatibility, increasing schema complexity.

## Test signals
Unit tests should exercise constructor options, request encoding, retry behavior, reply zeroing, non-200 response errors, bearer-token wrapping, and JSON compatibility. The adjacent test currently checks `UserAgent` option handling. This research pass did not run Go tests.
