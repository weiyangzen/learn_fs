# sources/sync-backup/kopia/cli/command_notification_template.go

## Purpose
Command group root and shared template-name argument for notification templates. It provides repository-backed autocomplete of available template names.

## APIs, Types, and Functions
Important APIs include types `commandNotificationTemplate`, `notificationTemplateNameArg`; functions/methods `setup`, `listNotificationTemplates`, `setup`; Kingpin command(s) template: Manage templates; arguments template: Template name.

## Control Flow, State, and Persistence
Control flow registers command(s) template: Manage templates, accepts arguments template: Template name, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches notification profiles/templates in repository metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, github.com/alecthomas/kingpin/v2, github.com/kopia/kopia/notification/notifytemplate, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/notification/notifytemplate, kopia/repo plus external packages context, github.com/alecthomas/kingpin/v2.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. nearby test file `sources/sync-backup/kopia/cli/command_notification_template_test.go` provides direct coverage.
