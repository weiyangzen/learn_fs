## sources/test-tools/syzkaller/pkg/lore-relay/relay_test.go

Purpose: integration-style unit tests for relay dashboard/email/Lore workflows.

Important APIs/types/functions: `mockSender`, `mockDashboard`, `TestMainScenario`, `TestRestartScenario`, error reply tests, unsupported command tests, `TestBackoff`, and helper command fixtures.

Control flow: mocks dashboard poll/confirm/command APIs and email sender, then exercises outgoing report publication, incoming command handling, restart idempotence, error replies, command silence policy, and retry timing.

State and persistence: mock slices capture sent emails and dashboard requests.

Dependencies and integration: validates relay behavior without real network/email.

Risks: mocks may not capture real Lore polling or DKIM verification edge cases.

Test signals: strong behavioral coverage for relay orchestration and dashboard request sequencing.
