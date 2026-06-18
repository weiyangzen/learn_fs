<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/ai.go -->
# sources/test-tools/syzkaller/dashboard/app/ai.go research

Purpose: dashboard UI and API implementation for AI workflow jobs, including manual job creation, agent polling, job completion, trajectory rendering, access filtering, staged reporting, patch iterations, bug labeling, and Gerrit upload.

Important APIs, types, and functions: UI structs include `uiAIJobsPage`, `ManualWorkflowSpec`, `uiAIJobPage`, `uiAIJob`, `uiJobReporting`, and patch history structs. Major functions include `manualAIWorkflows`, `handleAIJobsPage`, `handleAIJobCreate`, `handleAIJobPage/Post`, `buildAIJobPollArgs`, `apiAIJobPoll`, `pollAIJob`, `apiAIJobDone`, `autoCreateAIJobs`, `autoCreatePatchIterationJobs`, `buildPatchHistory`, `loadPatchLineage`, `collectChangelog`, `aiJobApplyLabels`, `workflowsForBug`, and `createGerritChange`.

Control flow: web handlers list jobs with cursor pagination, filter by workflow/aborted state, enforce namespace access, and render JSON or templates. Manual creation validates AI-action permission and workflow schemas, resolves kernel config input, and creates `aidb.Job` rows. Agent polling records liveness/workflows, prefers stale jobs, then patch iterations, then normal queued/auto-created jobs. Job completion stores results/errors, applies labels, finalizes patch iterations, optionally uploads Gerrit changes, and creates initial staged reportings for successful patching jobs.

State and persistence: persists jobs, reportings, comments, trajectories, journals, labels, bug crash references, pending workflow fields, and generated comments through Spanner (`aidb`) and App Engine datastore/text storage. UI formatting may resolve text blobs into args but does not persist them.

Dependencies and integration: integrates dashboard config, `dashapi`, `aidb`, AI workflow output types, App Engine datastore, templates, lore links, email formatting, Gerrit, VCS links, crash title classification, target metadata, and access control from `access.go`.

Risks: the file coordinates two storage systems and multiple external integrations, so idempotency and transaction boundaries matter. Workflow suffix authorization prevents clients from executing disallowed jobs. Patch-iteration selection is intentionally randomized and capped. Large JSON/result schema changes can break `castJobResults` parsing. Manual actions must not bypass staged-reporting constraints.

Test signals: AI job UI JSON/export, agent poll/done APIs, access filtering, retry/backoff behavior, label application, patch lineage/changelog formation, staged reporting transitions, comment debounce iteration creation, and Gerrit/log error paths.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/ai.go -->
