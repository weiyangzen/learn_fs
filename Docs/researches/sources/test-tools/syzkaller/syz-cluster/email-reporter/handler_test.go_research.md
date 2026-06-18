# sources/test-tools/syzkaller/syz-cluster/email-reporter/handler_test.go

## Purpose
Unit/integration tests for outgoing report emails and incoming command handling.

## Important APIs, types, and functions
Tests include `TestModerationReportFlow`, `TestReportInvalidationFlow`, `TestInvalidReply`, and `TestSyzTestFlow`. `setupHandlerTest` creates a test environment, controller server, dummy series/findings, reporter generator, reporter test server, fake sender, and configured `Handler`. `fakeSender` captures sent `sender.Email` values through a buffered channel.

## Control flow
The tests generate a moderation report, poll/send it, emulate command replies, and then verify subsequent reporting or absence of reporting. `TestSyzTestFlow` submits a patch-test command, confirms it is silent on success, fakes job completion, generates a report, and verifies the result email references the original user reply.

## State and persistence behavior
Uses in-memory/test Spanner and blob storage from `app.TestEnvironment`. Reporter state advances through real reporter APIs. Fake sender captures transient outgoing email state without external delivery.

## Dependencies and integration points
Exercises `pkg/controller`, `pkg/reporter`, `pkg/email`, `pkg/emailclient`, `pkg/db`, and API clients. It validates that email reporter behavior aligns with report generation and job submission.

## Risks and edge cases
The fake sender always returns `"email-id"` and never errors, so send-failure/ambiguous-delivery behavior is not covered. The tests validate selected email fields and body snippets but intentionally ignore full report body rendering in some paths.

## Test signals
Strong coverage for command semantics, recipient/CC/subject construction, moderation transition, invalidation, own-email suppression, forwarded own-email acceptance, and patch-test result reporting.
