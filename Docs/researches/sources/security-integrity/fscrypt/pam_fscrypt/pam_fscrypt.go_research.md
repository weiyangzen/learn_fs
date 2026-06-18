# sources/security-integrity/fscrypt/pam_fscrypt/pam_fscrypt.go

## Purpose
`pam_fscrypt.go` implements the exported PAM module hooks that copy login tokens, unlock fscrypt policies at session open, lock them at final session close, and rewrap login protectors after password changes.

## Important APIs, Types, and Functions
Constants define PAM data labels and module flags: `authtokLabel`, `pidLabel`, `debugFlag`, `lockPoliciesFlag`, `unlockOnlyFlag`, and `dropCachesFlag`. Core functions are `Authenticate`, `OpenSession`, `CloseSession`, `lockLoginPolicies`, `Chauthtok`, `setupUserKeyringIfNeeded`, `isUnsupportedFork`, `beginProvisioningOp`, and `endProvisioningOp`. Exported PAM symbols include `pam_sm_authenticate`, `pam_sm_setcred`, `pam_sm_open_session`, `pam_sm_close_session`, and `pam_sm_chauthtok`.

## Control Flow
`Authenticate` switches to the PAM user, saves the current PID, detects whether a login protector exists, and stores a locked copy of `AUTHTOK` for later session use. `OpenSession` increments the session count, switches to the PAM user, finds the login protector and policies needing unlock, detects unsupported fork-between-auth-and-session cases, prepares keyrings, unlocks the protector from stored `AUTHTOK`, then provisions each policy, temporarily regaining root for operations that need it. `CloseSession` decrements the count and, only for the last session and unless `unlock_only` is set, deprovisions login-protected policies and drops inode/dentry caches if user-keyring policies require it. `Chauthtok` unlocks the login protector with `OLDAUTHTOK` and rewraps it with new `AUTHTOK`.

## State and Persistence
PAM handle data stores the copied auth token and original PID. Session counts persist under `/run/fscrypt` via `run_fscrypt.go`. Policy provisioning changes kernel keyring state; protector rewrapping updates metadata through actions. Secrets are cleared from PAM data after session open.

## Dependencies and Integration Points
Integrates with `actions` protectors/policies, `crypto.NewKeyFromCString`, `keyring.UserKeyringID`, `pam.Handle`, and `security.DropFilesystemCache`. It is the bridge between system login/session/password lifecycle and fscrypt policy key provisioning.

## Risks
PAM modules run in sensitive login processes. The code has explicit fork detection because Go runtime after fork can deadlock, but detection may occur after Go code has already run. Correct privilege switching is critical. If `AUTHTOK` is missing, login-protected directories will not unlock. The deprecated flags are accepted but mostly no-ops, which can surprise older configurations.

## Test Signals
Direct tests are sparse; `run_test.go` only covers empty argument parsing. Behavior relies on integration with actions, keyring, filesystem metadata, PAM handle wrappers, and system-level PAM tests.
