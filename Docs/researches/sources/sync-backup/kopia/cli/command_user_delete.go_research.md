<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_user_delete.go -->
# sources/sync-backup/kopia/cli/command_user_delete.go

## Purpose
Implements `server users delete/remove/rm`, deleting a repository user profile.

## Important APIs, Types, And Functions
Defines `commandServerUserDelete`, `setup`, and `run`. `run` calls `user.DeleteUserProfile` and logs successful deletion.

## Control Flow
The command parses a required username and performs one repository writer operation.

## State And Persistence Behavior
Persistent mutation is removal of the user profile from repository metadata. Running servers may continue using cached credentials until refresh/restart, as noted by add/set but not repeated here.

## Dependencies And Integration Points
Depends on `internal/user` and repository writer action plumbing.

## Risks And Edge Cases
There is no confirmation prompt, so accidental deletion is possible. Error wrapping does not distinguish nonexistent user from other delete failures unless the underlying package does.

## Test Signals
Tests should cover successful delete, aliases, nonexistent users, and authentication failure after server refresh.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_user_delete.go -->
