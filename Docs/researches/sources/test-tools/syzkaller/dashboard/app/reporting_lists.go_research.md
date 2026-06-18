# sources/test-tools/syzkaller/dashboard/app/reporting_lists.go

## Purpose

`reporting_lists.go` implements monthly subsystem bug-list reminders. It periodically builds `SubsystemReport` datastore entities for configured subsystems, exposes those reports to reporting backends as `dashapi.BugListReport`, and applies commands that mark stages sent, upstream reports, or request regeneration.

## Important APIs, Types, and Functions

The main producer is `handleSubsystemReports`, which creates fresh reports. The main poller is `reportingPollBugLists`. Command handling is done by `reportingBugListCommand` and `findSubsystemReportByID`. Report construction and filtering are handled by `querySubsystemReport`, `queryMatchingBugs`, `makeSubsystemReportStats`, and `makeSubsystemReport`. Backend payload conversion is `reportingBugListReport`. Persistence helpers include `makeSubsystem`, `subsystemKey`, `subsystemReportKey`, `subsystemsRegistry`, `makeSubsystemRegistry`, `subsystemsRegistry.updatePoll`, `subsystemReportRegistry`, `makeSubsystemReportRegistry`, and `storeSubsystemReport`. IDs use `bugListReportingHash` with `bugListHashPrefix`.

## Control Flow

`handleSubsystemReports` loads known subsystem state, iterates namespaces with `Subsystems.Reminder`, builds a round-robin list of configured subsystems sorted by `ListsQueried`, skips recently reported subsystems based on `PeriodDays`, queries matching bugs, updates poll timestamps, and stores up to `maxNewListsPerNs` new reports per namespace. `querySubsystemReport` selects open bugs at the configured source reporting stage, skips stale, too-new, low-priority, recently discussed, and `NoRemindersLabel` bugs, balances reproducible and non-repro bugs, sorts by priority/crashes/title, applies optional moderation skipping, and records bug keys plus total/period stats.

`reportingPollBugLists` loads `ReportingState` and a report registry, then scans configured subsystem reports in stable subsystem order. It respects the source reporting daily limit and returns only stages whose reporting config type matches the caller. `reportingBugListReport` skips closed stages, skips missing configs, stops at already-reported or different-type stages, loads referenced bugs, and builds links and stats. Commands run in a transaction and update stage `Reported`, `Closed`, `ExtID`, `Link`, reporting quota, or subsystem `LastBugList`.

## State and Persistence Behavior

The file persists `Subsystem` entities keyed by namespace/name and child `SubsystemReport` entities keyed by creation time. `Subsystem` stores `ListsQueried` and `LastBugList`; `SubsystemReport` stores encoded bug keys, total and period stats, creation time, and one or two `SubsystemReportStage` entries. `storeSubsystemReport` closes all previous active reports for the subsystem before saving the new one. `reportingBugListCommand` also updates singleton `ReportingState` when a list is sent.

## Dependencies and Integration Points

It depends on namespace subsystem service configuration, `BugListReportingConfig`, reporting configs, datastore, `dashapi.BugListReport`, `hash`, subsystem maintainers, bug labels and priority, discussion summaries, and the generic reporting state used by normal bug reporting. Email handling calls these functions to send list mail and process list commands.

## Risks and Edge Cases

The lifecycle is stateful across cron ticks: a failed store or command can leave old reports active or cause repeated sends. `reportingPollBugLists` assumes `SourceReporting` exists; missing config would panic or nil dereference through `reporting.Name`. Stage skipping is intentional when moderation config disappears, but command handling must close skipped stages to avoid stuck reports. Encoded bug keys can become stale; `reportingBugListReport` fails if `db.GetMulti` cannot load them. Reports only include bugs currently at the expected reporting stage and access level, so reporting config changes can alter eligibility.

## Test Signals

Email and subsystem reminder tests in the package exercise list creation, sending, upstream/regenerate commands, and label set/unset commands against bug-list references. `main_test.go` provides subsystem classification and page coverage that underpins reminder selection.
