<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_session_list.go -->
# sources/sync-backup/kopia/cli/command_session_list.go

## Purpose
Implements hidden `kopia session list`, which prints active content sessions from a direct repository.

## Important APIs, Types, And Functions
Defines `commandSessionList` and `run`. It requires `repo.DirectRepository`, calls `ContentReader().ListActiveSessions`, and prints ID, user, host, start time, and checkpoint time.

## Control Flow
The direct repository read action opens the repo, `run` queries active sessions once, then formats each returned session on stdout.

## State And Persistence Behavior
It is read-only. The observed state is repository session metadata maintained by the content manager, not CLI-local state.

## Dependencies And Integration Points
Depends on direct repository access rather than server/client repository interfaces, and on shared timestamp formatting.

## Risks And Edge Cases
The command will not work through indirect/server repositories. Output is plain text only and may expose user/host details.

## Test Signals
Tests should set up active sessions or mock content reader behavior and verify formatting, empty lists, and error wrapping from `ListActiveSessions`.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_session_list.go -->
