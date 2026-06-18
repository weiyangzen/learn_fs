# sources/test-tools/syzkaller/dashboard/app/email_test.go

Purpose: comprehensive integration tests for syzbot email reporting, incoming command processing, mailing-list interactions, CC management, label/subsystem commands, forwarding, and anti-loop behavior.

Important tests: `TestEmailReport` is the main end-to-end scenario: first report formatting, mailing-list echo capture, opt-out/uncc, syz and C reproducer update emails, upstream transition, CC accumulation, invalid command replies, fix command persistence, builder pending commits, and new bug sequence after fix. Duplication tests cover dup/undup, cross-reporting restrictions, and title parsing variants. Error/loop tests verify replies only when syzbot is addressed appropriately and never to its own bounced replies. Other scenarios cover failed build reports, unfix behavior, manager CC/build-maintainer rules, strace wording, subject-title parsing, bug inference from mailing-list subject, report link capture, patch-testing access control, subsystem/label set/unset validation, archival forwarding for configured mailing lists/inboxes, duplicate forward suppression, and ignoring indirect commands found only through `Reported-by`.

Control flow under test: tests combine build upload, crash/build-error reports, outgoing mail polling, App Engine incoming mail POSTs, `#syz` commands, reporting-stage transitions, builder polling, commit uploads, context config overrides, and label inspections.

State and persistence behavior: heavily exercises `Bug`, `Crash`, `Build`, reporting state, CC lists, opt-out lists, labels, link/message IDs, commit-fix state, pending builder commits, and outgoing email queue. It also verifies text blobs behind external links for logs/configs/repros.

Dependencies and integration points: uses `dashapi`, `pkg/email`, target architecture metadata, test harness mail helpers, reporting/email implementation, label validation, subsystem services, manager config, monitored inbox config, and API clients.

Risks covered: malformed or indirect commands causing unwanted state changes, mail loops, wrong recipients/CC leakage, mailing-list subject ambiguity, cross-reporting dup mistakes, label validation errors, forwarded-command archival behavior, and report formatting regressions. Gaps are mostly around real mail transport and concurrent command races.
