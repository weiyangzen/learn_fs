<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/ai_report.go -->
# sources/test-tools/syzkaller/dashboard/app/ai_report.go research

Purpose: external AI patch-reporting command and polling API for integrations such as lore-relay.

Important APIs, types, and functions: functions include `apiAIReportCommand`, `handleUpstreamCommand`, `checkActionAuthorized`, `processUpstreamSubcommand`, `determineNextStage`, `handleRejectCommand`, `handleUnrejectCommand`, `handleCommentCommand`, `apiAIPollReport`, `makeNewReportResult`, `populateIterationReportResult`, `apiAIConfirmReport`, `handleCommandError`, and `lookupJobByExtReq`. Constant `SourceWebUI` names manual web-originated commands.

Control flow: command handling first performs idempotency checks by source/ext ID, looks up the reporting/job by root external ID, dispatches upstream/reject/unreject/comment subcommands, and converts expected domain errors into response `Error` strings while logging them for duplicate suppression. Upstream authorization checks optional allowed authors and DKIM, verifies the job is patch-upstreamable, determines the next configured AI stage, and records an upstream command/reporting. Polling scans pending reportings for an integration source, loads jobs and namespace stage config, converts patching or iteration results into `dashapi.ReportPollResult`, merges bug closure/reported-by links, chooses mailing-list recipients, and reports whether a later upstream stage is possible.

State and persistence: reads/writes Spanner `aidb` jobs, reportings, journals, comments, command logs, and published external IDs. Comment bodies are stored in dashboard text storage and referenced as `text://` URIs.

Dependencies and integration: connects `dashapi` external-report endpoints, namespace `AIConfig` stage settings, DKIM/auth metadata, email recipient formatting, lore/message IDs, App Engine text storage, and AI output schemas.

Risks: external commands are security sensitive; allowed-author plus DKIM enforcement is optional by namespace config and must be correct when enabled. Idempotency requires both `Source` and `MessageExtID`. Stage ordering rejects later-stage conflicts, which protects reporting consistency but can surprise operators after config changes.

Test signals: duplicate command no-ops, unauthorized command errors, reject/unreject/upstream state transitions, report-not-found mapping, poll output recipients/CC merging, patch metadata formatting, changelog creation for iterations, comment duplicate suppression, and publish confirmation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/ai_report.go -->
