# sources/test-tools/syzkaller/dashboard/app/subsystem_test.go

Purpose: integration tests for subsystem maintainer lookup, automatic subsystem refresh, user override preservation, and monthly subsystem reminder/report email generation and moderation.

Important tests: `TestSubsytemMaintainers`, `TestPeriodicSubsystemRefresh`, `TestOpenBugRevRefresh`, `TestClosedBugSubsystemRefresh`, `TestInvalidBugSubsystemRefresh`, `TestUserSubsystemsRefresh`, `TestNoUserSubsystemOverwrite`, `TestPeriodicSubsystemReminders`, `TestSubsystemRemindersModeration`, `TestSubsystemRemindersSkipModeration`, `TestSubsystemReportGeneration`, `TestSubsystemRemindersNoReport`, `TestNoRemindersWithDiscussions`, `TestSkipSubsystemReminders`, and `TestRemindersPriority`.

Control flow: setup creates builds/crashes with guilty files mapping to test subsystems, polls reports/emails, manually changes labels via inbound `#syz` email commands, advances mocked time, invokes `/cron/refresh_subsystems` and `/cron/subsystem_reports`, then asserts labels and exact email subjects/bodies. Reminder tests create multiple bugs across subsystems with different crash counts, repro levels, fix states, discussions, priorities, and no-reminder settings to validate sorting and filtering.

State and persistence: exercises datastore bug labels, subsystem revision/time fields, email sink state, monthly report history/regeneration, discussion records from `SaveDiscussion`, fix commit upload state, and user label overrides. Moderation flow first sends reports to moderation, then accepts `#syz upstream` to send public subsystem reports.

Dependencies and integration points: depends on `subsystem.go`, email parser and address context helpers, dashboard reporting APIs, cron handlers, discussion API, subsystem config in test namespaces, and `Ctx` time/config mutation helpers.

Risks: many assertions compare full email bodies, making wording/layout changes visible. Monthly report behavior is sensitive to time windows, active-vs-old crashes, discussion suppression, priority filtering, and exact recipient/moderation config. User-issued `#syz set` commands must map report references correctly even when quoted text surrounds commands.

Test signals: passing tests indicate automatic subsystem inference and monthly report generation remain stable, user subsystem choices are respected, moderation and skip-moderation hooks work, and reports avoid noise from inactive bugs, recent discussions, no-reminder labels, and unsupported subsystem configurations.
