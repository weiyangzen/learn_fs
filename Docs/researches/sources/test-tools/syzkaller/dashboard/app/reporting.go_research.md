# sources/test-tools/syzkaller/dashboard/app/reporting.go

## Purpose

`reporting.go` contains backend-independent bug reporting logic. It decides when bugs should be reported, builds `dashapi.BugReport` and `dashapi.BugNotification` payloads, tracks reporting quotas, applies incoming external status updates, handles duplicate validation, constructs full bug info, and provides shared datastore query helpers.

## Important APIs, Types, and Functions

Main polling functions are `reportingPollBugs`, `handleReportBug`, `needReport`, `reportingPollNotifications`, `handleReportNotif`, and `reportingPollClosed`. Notification generation is driven by `notificationGenerators`, `createLabelNotification`, `bugObsoletionReason`, `Bug.canBeObsoleted`, `Bug.obsoletePeriod`, and `createNotification`.

Report construction uses `currentReporting`, `createBugReport`, `crashBugReport`, `loadReproSyz`, `fillBugReport`, `managersToRepos`, `queryCrashesForBug`, and `findCrashForBug`. Incoming updates enter through `incomingCommand`, `incomingCommandImpl`, `incomingCommandTx`, `incomingCommandUpdate`, and `incomingCommandCmd`, and `checkBugStatus`. Duplicate safety is enforced by `checkDupBug`, `allowCrossReportingDup`, `getReportingIdx`, `findBugByReportingID`, and `findDupByTitle`. Reporting configuration migration is handled by `Bug.updateReportings`. Full external detail uses `loadFullBugInfo`, `prepareBisectionReport`, `prepareFixCandidateReport`, and `representativeCrashes`.

## Control Flow

Polling loads reporting state and open bugs, sorts by `bugReportSorter`, and returns at most three reports per poll to avoid memory pressure. `needReport` checks current reporting stage, requested backend type, already-reported repro level, namespace reporting delay, repro wait, missing report policy, crash count, and daily quota. If a bug is ready, `createBugReport` selects a representative crash, optionally substitutes a bisection crash, and fills a `dashapi.BugReport`.

Notification polling scans open reported bugs and applies ordered notification generators: embargo upstreaming, filter-skip upstreaming, obsoletion, bad fix commit, and configured label messages. Incoming commands normalize fix commit quoting, resolve bug/reporting IDs and duplicates, then run a cross-group datastore transaction that validates status, updates bug/reporting fields, records crash references, merges CC, updates repro level and activity, persists `Bug`, and saves `ReportingState`.

## State and Persistence Behavior

Persistent state centers on datastore `Bug`, `BugReporting`, `Crash`, `Build`, `Job`, and singleton `ReportingState` entities. `ReportingStateEntry.Sent` enforces daily reporting limits and resets by `timeDate`. Incoming updates mutate `Bug.Status`, `Closed`, `DupOf`, `Commits`, `FixTime`, `LastActivity`, `UNCC`, `BugReporting.Reported`, `Closed`, `Auto`, `ExtID`, `Link`, `CC`, `CrashID`, `ReproLevel`, `Labels`, and `OnHold`. Crash references are added or removed so crash purge/reporting accounting remains correct.

## Dependencies and Integration Points

This file is called by email reporting, external reporting APIs, job reporting, UI status rendering, public full bug info APIs, and tests. It depends on config reporting filters, App Engine datastore transactions, text storage, build loading, bisection/job helpers, email helpers, subsystem maintainers, asset creation, kernel repo metadata, and `dashapi` status/report types.

## Risks and Edge Cases

Reporting stage ordering and filtering are subtle: `currentReporting` skips unreported stages with `FilterSkip` but keeps reported skipped stages, and `updateReportings` forbids reordering while allowing insertions/deletions with dummy stages. Duplicate handling must prevent cycles, cross-namespace dups, self-dups, and unsafe cross-reporting dups. Obsoletion is probabilistic and capped by namespace or manager config. Incoming updates intentionally use many transaction attempts because email backends may not retry. Partial failures after external systems receive reports can create repeated notifications until `incomingCommand` or `jobReported` succeeds. Report construction depends on text blobs and builds still existing.

## Test Signals

`notifications_test.go` covers notification timing, obsoletion, bad commit reminders, and external notifications. Email and reporting tests elsewhere exercise incoming commands, duplicate/fix/update flows, repro-level reporting, job reports, and reporting migration. UI tests indirectly depend on `needReport` for status text.
