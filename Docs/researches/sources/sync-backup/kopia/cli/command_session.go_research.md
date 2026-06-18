<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_session.go -->
# sources/sync-backup/kopia/cli/command_session.go

## Purpose
Provides the hidden `kopia session` command namespace for repository session maintenance commands.

## Important APIs, Types, And Functions
Defines `commandSession` with a single `list` child, and `setup` registers the hidden parent and delegates to `commandSessionList.setup`.

## Control Flow
There is no runtime flow beyond CLI registration. Selecting `session list` enters the child command.

## State And Persistence Behavior
This file has no mutable or persistent state; active session information is read by the child command from repository content state.

## Dependencies And Integration Points
Depends only on local command registration abstractions and `command_session_list.go`.

## Risks And Edge Cases
Because it is hidden, regressions may be missed by normal help/command-surface tests. Adding more session subcommands requires this parent to be updated.

## Test Signals
A command discovery test can assert the hidden parent still accepts the `list` child and aliases from the child.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_session.go -->
