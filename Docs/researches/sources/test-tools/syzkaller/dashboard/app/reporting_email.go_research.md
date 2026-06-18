# sources/test-tools/syzkaller/dashboard/app/reporting_email.go

## Purpose

`reporting_email.go` implements the email backend for syzkaller reporting. It sends bug reports, job results, notifications, subsystem bug-list reminders, and coverage regression mail, and it processes inbound email commands, bounces, monitored inbox forwarding, and discussion archiving.

## Important APIs, Types, and Functions

`EmailConfig` is the reporting configuration type with `Type`, `Validate`, and `getSubject`. `initEmailReporting` registers cron and inbound mail routes and discovers configured mailing lists. Cron send paths are `handleCoverageReports`, `sendNsCoverageReport`, `coverageTable`, `handleEmailPoll`, `emailPollJobs`, `emailPollNotifications`, `emailPollBugs`, `emailPollBugLists`, `emailSendBugReport`, `emailSendBugListReport`, `emailSendBugNotif`, `emailReport`, `emailListReport`, `sendMailTemplate`, and `sendMailText`.

Inbound handling starts at `handleIncomingMail`, then routes to `processInboxEmail`, `processDiscussionEmail`, or `processIncomingEmail`. Identification and command helpers include `identifyEmail`, `loadBugInfo`, `bugInfoWithoutBugID`, `matchBugFromList`, `subjectTitleParser`, `handleBugCommand`, `handleTestCommand`, `handleSetCommand`, `handleUnsetCommand`, and `handleBugListCommand`. Address and reply utilities include `ownEmail`, `ownEmails`, `ownMailingLists`, `missingMailingLists`, `forwardEmail`, `replyTo`, `replyError`, `sanitizeCC`, `externalLink`, and `appURL`.

## Control Flow

`handleEmailPoll` checks emergency stop, sends completed job reports, sends notifications, sends new bug reports, then sends bug-list reports. Successful bug report delivery is followed by `incomingCommand` with `BugStatusOpen` and the observed repro level so the datastore records that the stage was reported. Notifications are translated into email bodies and then back into `incomingCommand` updates: upstream notifications close the current reporting stage, obsoletion marks invalid, label notifications record the label as sent, and bad commit reminders keep the bug open.

Inbound mail is parsed with syzkaller email helpers. Discussion addresses bypass emergency stop and are saved as discussion messages. Monitored inbox mail may be forwarded to required lists. Normal command mail identifies a bug by embedded reporting hash or by subject plus mailing list, filters duplicates from mailing lists, caps command counts, and applies commands through reporting updates or label mutations. `#syz test` creates patch test jobs when the bug is public and command syntax is valid. Bug-list commands operate on `SubsystemReport` stages or referenced bugs.

## State and Persistence Behavior

This file writes mail through App Engine mail and then records delivery effects in datastore through `incomingCommand`, `jobReported`, `reportingBugListCommand`, label update transactions, discussion saving, test request creation, and monitored inbox forwarding. It reads and writes no standalone email state, but it relies heavily on `Bug.Reporting`, `ReportingState`, `SubsystemReport`, `Discussion`, `Job`, and coverage DB records. `sendEmail` is a variable for test stubbing.

## Dependencies and Integration Points

The email backend integrates with App Engine mail and request contexts, `pkg/email` parsing/formatting, lore discussion typing, coverage DB, text templates from `mail_*.txt`, reporting core in `reporting.go`, subsystem bug-list reporting in `reporting_lists.go`, test job creation, discussion storage, and dashboard config.

## Risks and Edge Cases

Inbound email is adversarial input. The code defends against malformed messages, own-mail loops, duplicate mailing-list copies, missing or ambiguous bug IDs, command spam, sample command echoes, and commands not directly addressed to syzbot. Subject-based matching can be ambiguous and is intentionally conservative. Forwarding and missing-list logic mutates `msg.Cc` and can affect subsequent command updates. Sending mail before recording state means a datastore failure can cause duplicate sends on a later cron. `handleCoverageReports` logs errors per namespace but does not fail the whole HTTP request. Some error replies intentionally suppress details to avoid leaking internals.

## Test Signals

`notifications_test.go` verifies notification mail behavior and message bodies. Email-focused tests in the package cover commands, bounces, patch testing, labels, discussion handling, and report templates. `main_test.go` and `public_json_api_test.go` indirectly exercise email reporting IDs and links.
