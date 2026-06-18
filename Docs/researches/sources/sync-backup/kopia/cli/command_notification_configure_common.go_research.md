# sources/sync-backup/kopia/cli/command_notification_configure_common.go

## Purpose
Generic notification profile configuration helper. It loads any existing profile, validates sender type, merges typed options, optionally sends a test notification, and saves the resulting profile with severity.

## APIs, Types, and Functions
Important APIs include types `commonNotificationOptions`; functions/methods `setup`, `configureNotificationAction`, `mapKeys`; flags send-test-notification: Test the notification, min-severity: Minimum severity.

## Control Flow, State, and Persistence
Control flow binds flags send-test-notification: Test the notification, min-severity: Minimum severity, then runs through a direct repository write action. The implementation persists notification profile metadata. State and persistence: touches notification profiles/templates in repository metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, maps, slices, github.com/alecthomas/kingpin/v2, github.com/pkg/errors, github.com/kopia/kopia/notification, github.com/kopia/kopia/notification/notifyprofile, github.com/kopia/kopia/notification/sender, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/notification, kopia/notification/notifyprofile, kopia/notification/sender, kopia/repo plus external packages context, maps, slices, github.com/alecthomas/kingpin/v2, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
