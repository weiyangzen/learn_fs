<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_user_list.go -->
# sources/sync-backup/kopia/cli/command_user_list.go

## Purpose
Implements `server users list`/`ls`, listing repository user profiles as plain usernames or JSON array entries.

## Important APIs, Types, And Functions
Defines `commandServerUserList`, `setup`, and `runUserList`. It uses `user.ListUserProfiles` and shared `jsonList`.

## Control Flow
The command begins a JSON list wrapper, loads profiles, emits each full profile when `--json` is set or only the username otherwise, and closes the JSON list.

## State And Persistence Behavior
It is read-only and observes repository user profile manifests. JSON mode exposes full profile structs.

## Dependencies And Integration Points
Depends on `internal/user`, `json_output.go`, and repository reader action plumbing.

## Risks And Edge Cases
Plain output order follows `ListUserProfiles`; deterministic sorting depends on that package. JSON mode can leak password hash metadata to authorized users.

## Test Signals
Tests should cover empty and nonempty repositories, plain versus JSON output, alias behavior, and ordering if promised by user APIs.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_user_list.go -->
