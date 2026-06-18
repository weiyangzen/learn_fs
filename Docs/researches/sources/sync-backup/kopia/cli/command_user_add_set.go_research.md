<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_user_add_set.go -->
# sources/sync-backup/kopia/cli/command_user_add_set.go

## Purpose
Implements `server users add/create` and `server users set/update`, including password entry, password hash assignment, and repository user profile persistence.

## Important APIs, Types, And Functions
Key symbols are `commandServerUserAddSet`, `setup`, `getExistingOrNewUserProfile`, `runServerUserAddSet`, `errPasswordsDoNotMatch`, and `askConfirmPass`.

## Control Flow
Setup selects add or set mode, registers password flags and username arg, and uses a repository writer action. Execution loads a new or existing profile, applies plain password, hash, or prompted password, rejects no-op updates, saves the user profile, and logs that running servers need refresh or restart.

## State And Persistence Behavior
Persistent state is the repository user profile, including password hash. Plain passwords are transient and converted through `user.Profile.SetPassword`.

## Dependencies And Integration Points
Integrates `internal/user`, repository writer actions, terminal password prompting from `password.go`, and server auth reload expectations.

## Risks And Edge Cases
Providing both `--user-password` and `--user-password-hash` applies both in order, with the hash winning if set after password. Interactive prompting depends on stdin being a terminal. Bad hashes are rejected by `SetPasswordHash`.

## Test Signals
Tests should cover add versus set, no-op update, ask-password mismatch, plain password hashing, hash validation, and server refresh behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_user_add_set.go -->
