<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_notifications_test.go -->
# sources/sync-backup/kopia/cli/command_server_notifications_test.go

Purpose: end-to-end test that server-triggered snapshots emit configured webhook notifications and KopiaUI JSON notifications.

Important APIs/types/functions: `TestServerNotifications`, `httptest.NewServer`, `notification profile configure webhook`, `sender.Message`, `RunAndProcessStderrAsync`, and server snapshot control.

Control flow: the test starts an HTTP webhook receiver, creates a repository and snapshots under two identities, configures a webhook notification profile, starts the server with KopiaUI notifications enabled and a short shutdown grace period, triggers a server snapshot for one source, waits for an HTML webhook payload containing success CSS, and waits for a stderr JSON notification that decodes into `sender.Message`.

State/persistence behavior: configures notification profile state in the repository and starts a live server. Notification side effects are outbound HTTP POST and stderr JSON lines.

Dependencies/integration: spans notification profiles, server snapshot execution, webhook sender, UI notification output, and async server lifecycle. Risks/test signals: timing-sensitive 5-second waits; it validates success notification shape but not every notification field.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_notifications_test.go -->
