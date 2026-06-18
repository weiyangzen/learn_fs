# sources/test-tools/syzkaller/dashboard/app/reporting_external.go

## Purpose

`reporting_external.go` exposes the backend-independent reporting core to external dashboard API clients. It is a thin adapter between `dashapi` RPC request/response types and internal reporting, notification, closed-bug, update, and test-job functions.

## Important APIs, Types, and Functions

The exported adapter functions are `apiReportingPollBugs`, `apiReportingPollNotifications`, `apiReportingPollClosed`, `apiReportingUpdate`, and `apiNewTestJob`. They consume `dashapi.PollBugsRequest`, `dashapi.PollNotificationsRequest`, `dashapi.PollClosedRequest`, `dashapi.BugUpdate`, and `dashapi.TestPatchRequest`, and return corresponding response structs.

## Control Flow

Each polling function first checks `emergentlyStopped`; if stop is active or querying stop state fails, it returns an empty response and the error where applicable. Bug polling calls `reportingPollBugs` for the requested reporting type, then appends completed job reports from `pollCompletedJobs`. Notification polling returns `reportingPollNotifications`. Closed polling delegates to `reportingPollClosed`.

`apiReportingUpdate` has two paths. If `req.JobID` is set, it marks the job as reported with `jobReported` and returns a `BugUpdateReply` with `Error` set on failure. Otherwise it delegates to `incomingCommand` and translates `(ok, reason, err)` into `BugUpdateReply`. `apiNewTestJob` calls `handleExternalTestRequest`; user/input errors are returned in `ErrorText`, while non-input errors are also logged.

## State and Persistence Behavior

This file does not directly mutate datastore, but its delegates do. `reportingPollBugs` and `reportingPollNotifications` read bugs/reporting state. `pollCompletedJobs` reads completed jobs. `jobReported` marks job reporting state. `incomingCommand` mutates bug/reporting/crash state transactionally. `handleExternalTestRequest` creates test jobs or rejects invalid requests.

## Dependencies and Integration Points

It is integrated with the dashboard API transport layer that dispatches authenticated `dashapi` methods. It depends on emergency stop state, reporting core, job reporting, external patch-test request validation, and App Engine logging.

## Risks and Edge Cases

The adapter deliberately returns empty successful-looking poll responses during emergency stop so external pollers do not receive new work. Completed job report polling errors are logged but do not fail bug polling, which prevents one job error from blocking normal bug reports but can delay job result delivery. `apiReportingUpdate` treats job updates separately from bug updates; malformed requests containing both a `JobID` and bug fields will take the job path. External test job errors distinguish `BadTestRequestError` from internal errors to avoid over-logging invalid input.

## Test Signals

`notifications_test.go` uses the external notification path through `globalClient.pollNotifs` and `ReportingUpdate`. Broader API/reporting tests in the package exercise external bug polling, updates, job completion, and test job request behavior.
