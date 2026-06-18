# sources/sync-backup/kopia/cli/command_notification_template_list.go

## Purpose
Notification template listing command that enumerates custom notification templates stored in repository metadata.

## APIs, Types, and Functions
Important APIs include types `commandNotificationTemplateList`; functions/methods `setup`, `run`; Kingpin command(s) list: List templates.

## Control Flow, State, and Persistence
Control flow registers command(s) list: List templates, then runs through a repository reader action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches notification profiles/templates in repository metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, sort, github.com/pkg/errors, github.com/kopia/kopia/notification/notifytemplate, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/notification/notifytemplate, kopia/repo plus external packages context, sort, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
