# sources/test-tools/syzkaller/syz-cluster/email-reporter/email_workflow_test.go

## Purpose
Tests Lore poller integration with reporter reply recording and incoming email processing.

## Important APIs, types, and functions
`TestPollerIntegration` uses `setupHandlerTest`, `lore.NewTestLoreArchive`, `MakeLorePoller`, reporter `RecordReply`, and `Handler.ProcessPolledEmail`. It covers direct replies, own-email ignoring, indirect replies through root message IDs, report identification via email context, unrelated messages, and empty bug ID handling.

## Control flow
The test first sends and confirms a report, records the outgoing message ID, writes synthetic messages to a test Lore archive, polls them, then passes `PolledEmail` instances to the handler. It verifies idempotency by attempting to record the same reply again.

## State and persistence behavior
Uses the test environment's reporter storage for report/reply state and a temporary git-backed Lore archive. The poller state is local to temporary directories.

## Dependencies and integration points
Connects `pkg/email/lore` parsing/polling, syz-cluster reporter APIs, email config context prefix handling, and email reporter command handling. It validates the same path the production `main.go` uses when `LoreArchiveURL` is set.

## Risks and edge cases
The test is synthetic and does not exercise network fetching from real lore.kernel.org. It does cover subtle reply threading and bot-own-email filtering, which are high-value correctness points for avoiding loops and duplicate command processing.

## Test signals
Strong integration signal for incoming email idempotency, root message correlation, context-derived report IDs, and ignored unknown or own messages.
