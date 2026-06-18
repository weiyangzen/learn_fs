# sources/sync-backup/kopia/cli/command_notification_template_internal_test.go

## Purpose
Test coverage for `command_notification_template_internal` CLI behavior. It exercises command execution through the Kopia test environment and asserts output, repository state, and error handling for TestNotificationTemplatesAutocomplete.

## APIs, Types, and Functions
Important APIs include functions/methods `TestNotificationTemplatesAutocomplete`; tests TestNotificationTemplatesAutocomplete.

## Control Flow, State, and Persistence
Control flow registers a namespace or shared helper used by sibling commands, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches notification profiles/templates in repository metadata, temporary test repositories and captured CLI output. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports testing, github.com/stretchr/testify/require, github.com/kopia/kopia/internal/repotesting. It integrates with Kopia repository internals such as kopia/internal/repotesting plus external packages testing, github.com/stretchr/testify/require.

## Risks and Test Signals
Risks and test signals: test signals come from named tests TestNotificationTemplatesAutocomplete.
