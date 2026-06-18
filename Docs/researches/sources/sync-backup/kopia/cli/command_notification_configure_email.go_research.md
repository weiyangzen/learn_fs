# sources/sync-backup/kopia/cli/command_notification_configure_email.go

## Purpose
Email notification profile configuration command. It registers SMTP/from/to/cc/bcc and message format flags and delegates merge/save behavior to the common notification helper.

## APIs, Types, and Functions
Important APIs include types `commandNotificationConfigureEmail`; functions/methods `setup`; Kingpin command(s) email: E-mail notification.; flags smtp-server: SMTP server, smtp-port: SMTP port, smtp-identity: SMTP identity, smtp-username: SMTP username, smtp-password: SMTP password, mail-from: From address, mail-to: To address, mail-cc: CC address, format: Format of the message.

## Control Flow, State, and Persistence
Control flow registers command(s) email: E-mail notification., binds flags smtp-server: SMTP server, smtp-port: SMTP port, smtp-identity: SMTP identity, smtp-username: SMTP username, smtp-password: SMTP password, mail-from: From address, mail-to: To address, mail-cc: CC address, plus 1 more, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches notification profiles/templates in repository metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports github.com/kopia/kopia/notification/sender, github.com/kopia/kopia/notification/sender/email. It integrates with Kopia repository internals such as kopia/notification/sender, kopia/notification/sender/email.

## Risks and Test Signals
Risks and test signals: secret-bearing options should avoid accidental output and preserve typed config. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
