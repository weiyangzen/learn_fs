# sources/test-tools/syzkaller/syz-cluster/pkg/report/email.go

## Purpose
Renders session reports into email body text.

## Important APIs, Types, and Functions
Render and embedded templateFS for template.txt and test_reply_template.txt.

## Control Flow
Chooses bug or patch-test template, parses templates, executes with Report and EmailConfig.

## State and Persistence
No persistence; transforms API report state into outbound message text.

## Dependencies and Integration Points
Integrates api.SessionReport, app.EmailConfig, embedded text templates, and reporter-generated report data.

## Risks and Edge Cases
Risks include template/schema drift and golden files masking regressions if regenerated without review.

## Test Signals
email_test.go golden-tests user-visible email bodies.
