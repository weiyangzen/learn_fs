# sources/test-tools/syzkaller/syz-cluster/pkg/report/email_test.go

## Purpose
Golden tests for report email rendering.

## Important APIs, Types, and Functions
TestRender and -write flag.

## Control Flow
Loads JSON fixtures, toggles moderation for bug reports, renders, and compares expected text files.

## State and Persistence
Reads fixtures; optional -write rewrites golden outputs.

## Dependencies and Integration Points
Integrates api.SessionReport, app.EmailConfig, embedded text templates, and reporter-generated report data.

## Risks and Edge Cases
Risks include template/schema drift and golden files masking regressions if regenerated without review.

## Test Signals
email_test.go golden-tests user-visible email bodies.
