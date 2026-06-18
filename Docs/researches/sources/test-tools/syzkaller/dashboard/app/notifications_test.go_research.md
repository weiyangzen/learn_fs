# sources/test-tools/syzkaller/dashboard/app/notifications_test.go

## Purpose

`notifications_test.go` verifies notification behavior for the backend-independent reporting logic and the email/external reporting adapters. It focuses on upstreaming notifications, bad fixing commit reminders, automatic obsoletion, and external notification polling.

## Important APIs, Types, and Functions

The tests use the same dashboard test harness plus `dashapi` update/poll types. Key test cases include `TestEmailNotifUpstreamEmbargo`, `TestEmailNotifUpstreamSkip`, `TestEmailNotifBadFix`, `TestBugObsoleting`, `TestEmailNotifObsoleted`, `TestEmailNotifNotObsoleted`, `TestEmailNotifObsoletedManager`, `TestExtNotifUpstreamEmbargo`, and `TestExtNotifUpstreamOnHold`.

## Control Flow

Email notification tests create bugs in staged reportings, poll the first bug report, advance fake time past configured periods, and then poll email again to observe notification messages and follow-up reports. The bad-fix test sends an inbound `#syz fix` command, advances past the 90-day bad commit notification period, and validates the generated body including tested tree information. Obsoletion tests upstream bugs, create activity or fresh crashes, then advance time to verify which bugs are invalidated and which remain open. External notification tests use `globalClient.pollNotifs` and `ReportingUpdate` to verify `BugNotifUpstream` behavior outside email.

## State and Persistence Behavior

These tests exercise persistent `Bug.Reporting` fields such as `Reported`, `Closed`, `OnHold`, `Auto`, `CC`, and reporting IDs; bug status transitions; commit metadata; manager/build records; discussion/activity timestamps; and reporting quota state indirectly. Time is controlled through `c.advanceTime`, which is essential because notification generation depends on embargo, resend, obsoletion, and bad-commit periods.

## Dependencies and Integration Points

The suite covers interaction among `reportingPollNotifications`, `createNotification`, `emailSendBugNotif`, `incomingCommand`, email address context encoding, `loadRepos`, manager config obsoleting overrides, and external polling APIs. It also depends on configured staged reportings and manager/repository fixtures.

## Risks and Test Signals

These tests provide strong signals for timing-sensitive behavior. They ensure embargo upstreaming does not happen early, auto-upstream respects repro/filter conditions, bad commit reminders include actionable text and repeat only after the resend period, obsoletion CC lists differ by reporting stage, new crashes can recreate obsolete bugs, and `OnHold` suppresses external upstream notifications. Gaps remain around label notifications, notification failures from missing build/crash data, and exact interactions with manually set labels or subsystem maintainers.
