# sources/sync-backup/kopia/cli/command_notification_configure_webhook.go

## Purpose
Webhook notification profile configuration command. It parses endpoint, HTTP method, repeated headers, and format options before using the common profile save/test path.

## APIs, Types, and Functions
Important APIs include types `commandNotificationConfigureWebhook`; functions/methods `setup`; Kingpin command(s) webhook: Webhook notification.; flags endpoint: SMTP server, method: HTTP Method, http-header: HTTP Header (key:value), format: Format of the message.

## Control Flow, State, and Persistence
Control flow registers command(s) webhook: Webhook notification., binds flags endpoint: SMTP server, method: HTTP Method, http-header: HTTP Header (key:value), format: Format of the message, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches notification profiles/templates in repository metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports net/http, strings, github.com/alecthomas/kingpin/v2, github.com/pkg/errors, github.com/kopia/kopia/notification/sender, github.com/kopia/kopia/notification/sender/webhook. It integrates with Kopia repository internals such as kopia/notification/sender, kopia/notification/sender/webhook plus external packages net/http, strings, github.com/alecthomas/kingpin/v2, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
