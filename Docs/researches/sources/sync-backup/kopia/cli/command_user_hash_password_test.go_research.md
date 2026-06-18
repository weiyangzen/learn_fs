<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_user_hash_password_test.go -->
# sources/sync-backup/kopia/cli/command_user_hash_password_test.go

## Purpose
End-to-end test for hashed repository-user passwords, including server authentication with a hash-created user and password rotation.

## Important APIs, Types, And Functions
`TestServerUserHashPassword` creates a repo, hashes a password, rejects a bad hash, adds a user by hash, starts a TLS server, connects as that user, hashes a second password, updates the user, refreshes the server, and reconnects with the new password.

## Control Flow
The flow uses in-process runners, `testutil.ServerParameters`, server stderr parsing, server-control refresh, and a separate client environment without inherited repository password.

## State And Persistence Behavior
Persistent state includes repository user profiles and password hashes. The running server caches user credentials until refreshed.

## Dependencies And Integration Points
Integrates user hash/add/set commands, server start TLS/random control password, repo connect server, and server refresh.

## Risks And Edge Cases
The test is timing-sensitive around server startup and credential refresh. It depends on stderr parsing for server address, fingerprint, and control password.

## Test Signals
Strong signal for user-hash compatibility and live server authentication. It does not test interactive password prompting.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_user_hash_password_test.go -->
