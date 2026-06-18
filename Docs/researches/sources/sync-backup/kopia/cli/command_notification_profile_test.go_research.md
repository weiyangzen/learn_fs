# sources/sync-backup/kopia/cli/command_notification_profile_test.go

## Purpose
Test coverage for `command_notification_profile` CLI behavior. It exercises command execution through the Kopia test environment and asserts output, repository state, and error handling for TestNotificationProfile, TestNotificationProfile_WebHook.

## APIs, Types, and Functions
Important APIs include functions/methods `TestNotificationProfile`, `TestNotificationProfile_WebHook`; tests TestNotificationProfile, TestNotificationProfile_WebHook.

## Control Flow, State, and Persistence
Control flow registers a namespace or shared helper used by sibling commands, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches notification profiles/templates in repository metadata, temporary test repositories and captured CLI output. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports testing, github.com/stretchr/testify/require, github.com/kopia/kopia/internal/testutil, github.com/kopia/kopia/notification/notifyprofile, github.com/kopia/kopia/notification/sender/webhook, github.com/kopia/kopia/tests/testenv. It integrates with Kopia repository internals such as kopia/internal/testutil, kopia/notification/notifyprofile, kopia/notification/sender/webhook, kopia/tests/testenv plus external packages testing, github.com/stretchr/testify/require.

## Risks and Test Signals
Risks and test signals: test signals come from named tests TestNotificationProfile, TestNotificationProfile_WebHook.
