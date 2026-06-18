<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_user_hash_password.go -->
# sources/sync-backup/kopia/cli/command_user_hash_password.go

## Purpose
Implements `server users hash-password`/`hash`, producing a repository user password hash that can be passed to add/set.

## Important APIs, Types, And Functions
Defines `commandServerUserHashPassword`, `setup`, and `runServerUserHashPassword`. It calls `askConfirmPass` when no password flag is provided and `user.HashPassword` to generate the encoded hash.

## Control Flow
The command intentionally requires a connected repository through repository writer action even though the current hashing implementation does not use it, preserving future compatibility.

## State And Persistence Behavior
No repository data is changed. The output password hash is printed to stdout; input password is held in memory in the command struct.

## Dependencies And Integration Points
Depends on `internal/user` hashing and shared password prompting/output helpers.

## Risks And Edge Cases
Hash output is sensitive and can be captured in shell history or logs if mishandled. Interactive mode depends on terminal password input. Future hash implementations may need repository parameters.

## Test Signals
Tests cover hash generation, using the hash to create/update a user, server refresh, and connecting with the resulting password.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_user_hash_password.go -->
