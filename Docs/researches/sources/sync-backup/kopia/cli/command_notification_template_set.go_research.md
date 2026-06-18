# sources/sync-backup/kopia/cli/command_notification_template_set.go

## Purpose
Notification template set command that reads replacement template text from stdin, file, or editor and saves it as a repository template override.

## APIs, Types, and Functions
Important APIs include types `commandNotificationTemplateSet`; functions/methods `setup`, `run`, `launchEditor`; Kingpin command(s) set: Set the notification template; flags from-stdin: Read new template from stdin, from-file: Read new template from file, editor: Edit template using default editor.

## Control Flow, State, and Persistence
Control flow registers command(s) set: Set the notification template, binds flags from-stdin: Read new template from stdin, from-file: Read new template from file, editor: Edit template using default editor, then runs through a repository writer action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches notification profiles/templates in repository metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, io, os, github.com/pkg/errors, github.com/kopia/kopia/internal/editor, github.com/kopia/kopia/notification/notifytemplate, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/internal/editor, kopia/notification/notifytemplate, kopia/repo plus external packages context, io, os, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: external editor flow must reject invalid or unchanged JSON safely. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
