<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_user_info.go -->
# sources/sync-backup/kopia/cli/command_user_info.go

## Purpose
Implements `server users info`, printing a repository user profile as indented JSON.

## Important APIs, Types, And Functions
Defines `commandServerUserInfo`, `setup`, and `run`. `run` uses `user.GetUserProfile`, `json.MarshalIndent`, and stdout.

## Control Flow
After parsing the required username, the command loads the profile and serializes it directly.

## State And Persistence Behavior
It is read-only but can expose user profile metadata, including password-hash representation, to stdout.

## Dependencies And Integration Points
Depends on `internal/user`, repository reader action plumbing, and Go JSON encoding.

## Risks And Edge Cases
Output shape is the raw user profile struct, so changes in `user.Profile` fields affect CLI compatibility. Sensitive data exposure is intentional but should be access-controlled by repository access.

## Test Signals
Tests should cover existing and missing users, JSON validity, and whether sensitive fields are present as expected.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_user_info.go -->
