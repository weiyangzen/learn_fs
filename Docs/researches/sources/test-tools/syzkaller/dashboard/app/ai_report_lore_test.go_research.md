<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/ai_report_lore_test.go -->
# sources/test-tools/syzkaller/dashboard/app/ai_report_lore_test.go research

Purpose: integration tests for AI report publication and command/comment handling through lore-relay.

Important APIs, types, and functions: tests include `TestAILoreIntegration`, `TestAILoreIntegrationReject`, `TestAILoreUnknownMessageID`, `TestAILoreIntegrationComment`, and `TestAILoreIteration`, plus `integrationMockSender`. They use `NewSpannerCtx`, `lore.NewTestLoreArchive`, `lore.NewPoller`, `lorerelay.NewRelay`, dashboard agent/global clients, and `dashapi` AI requests.

Control flow: tests create AI patch jobs, finish them with patch metadata, poll the dashboard to send moderation/public emails, inject lore archive messages containing `#syz upstream`, `#syz reject`, `#syz unreject`, and plain comments, then poll lore/dashboard again to assert resulting emails, errors, reportings, comments, and iteration jobs. Iteration tests advance fake time past debounce windows, poll an agent for patch-iteration work, complete replies or patch v2/v3, and verify stage/version-specific subjects and inherited sign-off behavior.

State and persistence: uses temporary Git-backed lore archives and Spanner/dashboard test state. `integrationMockSender` captures sent email structs and returns deterministic mock message IDs.

Dependencies and integration: exercises `ai_report.go`, `ai.go` iteration logic, lore polling, lore-relay command parsing, email formatting, trajectory-assisted tags, comment storage, DKIM/own-email flags, and dashboard API clients.

Risks: these are broad integration tests and can fail due behavior changes in email formatting, message threading, fake-time ordering, or lore archive polling. The tests explicitly handle non-deterministic comment ordering when timestamps match.

Test signals: expected email counts/recipients/subjects/bodies, no duplicate error replies after relay restart, silence on unknown message IDs, reject/unreject/upstream failure messages, no iteration for rejected patches, stored comment body/own-email flags, patch-history fixes propagation, and version reset per reporting stage.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/ai_report_lore_test.go -->
