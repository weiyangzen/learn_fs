# sources/sync-backup/kopia/cli/command_notification_profile_show.go

## Purpose
Notification profile show command that displays a named profile either as raw configuration or formatted summary.

## APIs, Types, and Functions
Important APIs include types `commandNotificationProfileShow`; functions/methods `setup`, `run`; Kingpin command(s) show: Show notification profile; flags raw: Raw output.

## Control Flow, State, and Persistence
Control flow registers command(s) show: Show notification profile, binds flags raw: Raw output, then runs through a repository reader action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches notification profiles/templates in repository metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, github.com/pkg/errors, github.com/kopia/kopia/notification, github.com/kopia/kopia/notification/notifyprofile, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/notification, kopia/notification/notifyprofile, kopia/repo plus external packages context, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
