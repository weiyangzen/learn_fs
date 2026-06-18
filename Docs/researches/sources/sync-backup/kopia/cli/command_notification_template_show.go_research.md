# sources/sync-backup/kopia/cli/command_notification_template_show.go

## Purpose
Notification template show command that renders custom or original templates, optionally converting markdown/template output to HTML and opening it.

## APIs, Types, and Functions
Important APIs include types `commandNotificationTemplateShow`; functions/methods `setup`, `run`; Kingpin command(s) show: Show template; flags format: Template format, original: Show original template, html: Convert the output to HTML.

## Control Flow, State, and Persistence
Control flow registers command(s) show: Show template, binds flags format: Template format, original: Show original template, html: Convert the output to HTML, then runs through a repository reader action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches notification profiles/templates in repository metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, os, path/filepath, strings, github.com/pkg/errors, github.com/skratchdot/open-golang/open, github.com/kopia/kopia/notification/notifytemplate, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/notification/notifytemplate, kopia/repo plus external packages context, os, path/filepath, strings, github.com/pkg/errors, plus 1 more.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
