<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/admin.go -->
# sources/test-tools/syzkaller/dashboard/app/admin.go research

Purpose: administrative and migration handlers for dashboard maintenance, bisection/job repair, datastore cleanup, email sending, bug-field backfills, crash-priority regeneration, and commit-info refresh.

Important APIs, types, and functions: functions include `handleInvalidateBisection`, `dropNamespace`, `dropNamespaceReportingState`, `dropEntities`, `restartFailedBisections`, `updateBugReporting`, `updateCrashPriorities`, `setMissingBugFields`, `adminSendEmail`, `updateHeadReproLevel`, `updateBatch`, and `forceCommitInfoUpdate`.

Control flow: most handlers first require admin access, parse request parameters, query datastore entities, print dry-run or progress output, and apply batched transactional updates through `updateBatch`. Destructive namespace deletion is intentionally disconnected from handlers and defaults to `dryRun := true`. Bisection restart lists failed jobs and only applies when `apply=yes`. Crash-priority/head-repro updates recompute derived fields from existing bugs, crashes, builds, and repro state.

State and persistence: can update or delete datastore entities, reporting state, jobs, bugs, crashes, and text-like entities. Some operations send email or restart bisection jobs. `updateBatch` writes in XG transactions in batches of 20.

Dependencies and integration: depends on App Engine datastore/log/mail, dashboard job/bug/build/crash models, reporting state, text storage, bisection invalidation, and admin HTTP routing where connected.

Risks: several functions are dangerous migrations with comments warning there is no undo. Admin checks are essential for connected handlers, while unconnected helpers rely on `runtime.KeepAlive` to avoid dead-code warnings. Panics inside batch transforms can abort maintenance transactions.

Test signals: admin-only rejection, dry-run output for namespace drops, job error listing without apply, transactional update counts, successful recomputation of repro levels/crash priorities, and no deadcode failures due `runtime.KeepAlive`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/admin.go -->
