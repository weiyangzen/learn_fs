# sources/sync-backup/kopia/cli/command_notification_profile.go

## Purpose
Command group root and shared profile-name flag for notification profiles. It also supplies autocomplete by listing profiles from the repository.

## APIs, Types, and Functions
Important APIs include types `commandNotificationProfile`, `notificationProfileFlag`; functions/methods `setup`, `setup`, `listNotificationProfiles`; Kingpin command(s) profile: Manage notification profiles; flags profile-name: Profile name.

## Control Flow, State, and Persistence
Control flow registers command(s) profile: Manage notification profiles, binds flags profile-name: Profile name, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches notification profiles/templates in repository metadata. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, strings, github.com/alecthomas/kingpin/v2, github.com/kopia/kopia/notification/notifyprofile, github.com/kopia/kopia/repo. It integrates with Kopia repository internals such as kopia/notification/notifyprofile, kopia/repo plus external packages context, strings, github.com/alecthomas/kingpin/v2.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. nearby test file `sources/sync-backup/kopia/cli/command_notification_profile_test.go` provides direct coverage.
