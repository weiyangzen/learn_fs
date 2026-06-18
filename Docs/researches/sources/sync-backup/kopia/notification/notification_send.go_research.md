<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/notification/notification_send.go -->
# sources/sync-backup/kopia/notification/notification_send.go

- Purpose: Sends Kopia notifications through local repository-configured senders or remote server notification APIs.
- Important APIs/types/functions: `AdditionalSenders`, `TemplateArgs`, `Severity`, severity constants, `SeverityToNumber`, `SeverityToString`, `notificationSendersFromRepo`, `Send`, `SendInternal`, `MakeTemplateArgs`, `SendTo`, `SendTestNotification`.
- Control flow: `Send` forwards JSON event args to remote repositories when possible; otherwise `SendInternal` loads sender profiles by severity, appends global additional senders, and calls `SendTo`. `SendTo` resolves and parses a template, executes it with build/host/event args, parses headers/body into a sender message, sets severity, and sends.
- State and persistence: Profiles/templates persist in repository manifests; `AdditionalSenders` is global process state; event args serialize to JSON for remote notification transport.
- Dependencies and integration points: Integrates `notifydata`, `notifyprofile`, `notifytemplate`, `sender`, `repo.RemoteNotifications`, and logging.
- Risks and edge cases: `Send` logs and suppresses errors; global `AdditionalSenders` can affect tests/plugins; template parse/execute errors abort a sender.
- Test signals: Server integration test exercises remote notifications; template tests exercise rendering but sender selection has limited direct tests here.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/notification/notification_send.go -->
