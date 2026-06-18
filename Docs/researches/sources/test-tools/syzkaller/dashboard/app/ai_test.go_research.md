# sources/test-tools/syzkaller/dashboard/app/ai_test.go

## Purpose

`ai_test.go` validates the dashboard's AI job creation, polling, namespace authorization, UI actions, trajectory logging, workflow registration, stale job recovery, and manual job creation paths. It sits above the AIDB package and below real external services, using dashboard clients to exercise the API and UI surfaces end to end.

## Important tests and APIs

- `TestAIMigrations` validates Spanner DDL up/down statements are syntax-correct and idempotent.
- `TestAIBugWorkflows` verifies active workflow discovery for bugs based on available agents, workflow type, and agent freshness.
- `TestAIRestrictedClient` and `TestAIJobNamespaces` cover API client restrictions by workflow suffix and namespace allowlists, including trajectory and completion authorization.
- `TestAIJob`, `TestAIAssessmentKCSAN`, `TestAIJobActions`, and `TestAIJobCustomCommit` validate created job args, UI review actions, trajectory spans, finished result handling, and custom base commit propagation.
- `TestAIJobAutoCreate`, `TestAIPendingJobs`, and `TestAIJobParallelPoll` cover automatic job creation, pending workflow fast-path behavior, and transactional duplicate prevention under concurrent polling.
- `TestAIAgentLastActive`, `TestAIAgentRestart`, and `TestAIAgentJobOvertake` validate agent heartbeat, restarted-agent recovery, and stale-job reassignment after inactivity.
- `TestAIManualJobCreate`, `TestAIReproCJobCreateFromBugPage`, `TestAIJobRestart`, and `TestManualAIWorkflows` cover manual UI-created jobs, restart restrictions, and empty manual workflow config behavior.

## Control flow and state behavior

The tests generally create a Spanner-enabled context, upload a build to App Engine datastore, report crashes to create dashboard bugs, then use `AIJobPoll` to register active workflows and claim jobs. When a workflow applies to a bug, a Spanner `Jobs` row is created or claimed and returned as `dashapi.AIJobPollResp` with structured `Args`. The tests verify these args include crash data, repro data, target platform, kernel and syzkaller revisions, and AI base repository settings.

Agent polling persists `Agents.LastActive` and `Workflows` rows. Job claiming updates `Jobs.Started`, `AgentName`, and `CodeRevision`. Completion through `AIJobDone` sets `Finished`, `Error`, and `Results`; UI correctness actions set `Correct` and write journal history. Stale job tests advance mocked time to trigger `NextStaleJob`, which aborts the old job and clones a replacement with equivalent workflow and args.

Manual job creation validates form input before writing jobs without an existing bug. Restart tests only allow failed non-iteration jobs to clone into a fresh job and reject running, successful, public, and patch-iteration restarts.

## Dependencies and integration points

The file uses `aidb` CRUD calls, `dashapi` AI methods, `pkg/aflow/ai` workflow constants, `pkg/aflow/trajectory`, `prog.GitRevision`, App Engine/datastore-backed dashboard helpers, and `errgroup` for concurrent poll validation. It integrates both HTTP UI routes (`/ai_job`, `/ains/ai`, `/bug`) and API methods (`AIJobPoll`, `AIJobDone`, `AITrajectoryLog`).

## Risks and edge cases

Key risks include duplicate job creation under concurrent polling, restricted clients seeing jobs outside their namespace or workflow suffix, stale running jobs never being recovered, and incorrect job args causing agents to work on the wrong source. The tests also cover subtle UI authorization behavior: public users are redirected, regular users can create/review in allowed contexts, and restricted API clients are blocked from trajectory or completion on unauthorized namespaces.

## Test signals

The file is broad regression coverage for AI jobs. It checks both successful and negative paths, uses direct Spanner reads to confirm persisted fields, validates JSON/export output for job pages, and uses concurrent goroutines to verify transactional uniqueness of job assignment.
