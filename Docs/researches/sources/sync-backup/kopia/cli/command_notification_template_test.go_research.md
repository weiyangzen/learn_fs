# sources/sync-backup/kopia/cli/command_notification_template_test.go

## Purpose
Test coverage for `command_notification_template` CLI behavior. It exercises command execution through the Kopia test environment and asserts output, repository state, and error handling for TestNotificationTemplates.

## APIs, Types, and Functions
Important APIs include functions/methods `TestNotificationTemplates`, `verifyTemplateContents`, `verifyHasLine`; tests TestNotificationTemplates.

## Control Flow, State, and Persistence
Control flow registers a namespace or shared helper used by sibling commands, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches notification profiles/templates in repository metadata, temporary test repositories and captured CLI output. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, os, slices, strings, testing, github.com/stretchr/testify/require, github.com/kopia/kopia/internal/editor, github.com/kopia/kopia/notification/notifytemplate, github.com/kopia/kopia/tests/testenv. It integrates with Kopia repository internals such as kopia/internal/editor, kopia/notification/notifytemplate, kopia/tests/testenv plus external packages context, os, slices, strings, testing, plus 1 more.

## Risks and Test Signals
Risks and test signals: external editor flow must reject invalid or unchanged JSON safely. test signals come from named tests TestNotificationTemplates.
