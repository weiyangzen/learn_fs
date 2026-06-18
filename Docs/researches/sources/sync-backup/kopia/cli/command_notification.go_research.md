# sources/sync-backup/kopia/cli/command_notification.go

## Purpose
Command group root for notification configuration. It registers profile, template, and sender-specific configuration subcommands.

## APIs, Types, and Functions
Important APIs include types `commandNotification`; functions/methods `setup`; Kingpin command(s) notification: Notifications.

## Control Flow, State, and Persistence
Control flow registers command(s) notification: Notifications, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches notification profiles/templates in repository metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: depends on sibling CLI command registration and shared app service interfaces in the `cli` package.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
