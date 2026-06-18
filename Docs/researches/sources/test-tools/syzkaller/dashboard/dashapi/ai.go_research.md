# sources/test-tools/syzkaller/dashboard/dashapi/ai.go Research

## Purpose
This file extends the dashboard API client with AI-agent job polling, trajectory logging, and AI-assisted external report command/poll/confirmation endpoints.

## Important APIs and types
- AI job flow: `AIJobPollReq`, `AIWorkflow`, `AIJobPollResp`, `AIJobDoneReq`, `AITrajectoryReq`, plus `Dashboard.AIJobPoll`, `AIJobDone`, and `AITrajectoryLog`.
- External report flow: `SendExternalCommandReq` with mutually exclusive `Upstream`, `Reject`, `Unreject`, or `Comment` commands; `PollExternalReportReq/Resp`; `ReportPollResult`; `NewReportResult`; `ReplyResult`; and `ConfirmPublishedReq`.
- `ErrReportNotFound` maps a dashboard string error in `SendExternalCommandResp.Error` to a typed Go sentinel.

## Control flow
Each method is a thin wrapper around `Dashboard.Query`, supplying a method string such as `ai_job_poll`, `ai_report_command`, or `ai_confirm_report`. `AIReportCommand` adds one semantic step: after transport success, it converts the response error string `report not found` into `ErrReportNotFound`.

## State and persistence
No local state is stored. Job state, trajectories, report publication state, patch metadata, and external IDs live on the dashboard service. Request/response structs are JSON-encoded by `dashapi.go`.

## Dependencies and integration points
Depends on `pkg/aflow/ai` for workflow and fixes-tag types, `pkg/aflow/trajectory` for spans, and the base dashboard client transport. It integrates AI agents, Lore/email patch workflows, and dashboard reporting entities.

## Risks
`Args` and `Results` use `map[string]any`, so schema errors are detected only at runtime by the server or consumers. The request requires only one command pointer to be set but this invariant is not enforced client-side. String matching for `ErrReportNotFound` is fragile if the server text changes.

## Test signals
Tests should cover method strings, JSON compatibility, the one-command invariant, and `ErrReportNotFound` mapping. No dedicated tests were present in this file; existing transport behavior is inherited from `dashapi.go`.
