# sources/security-integrity/fscrypt/pam/login.go

## Purpose
`pam/login.go` verifies whether a supplied `crypto.Key` matches a user's login passphrase by running a PAM authentication transaction.

## Important APIs, Types, and Functions
`ErrPassphrase` reports failed authentication. Exported cgo callbacks `userInput` and `passphraseInput` provide PAM conversation responses. `IsUserLoginToken(username, token, quiet)` is the public verification API. Global `tokenLock` and `tokenToCheck` serialize callback state.

## Control Flow
`IsUserLoginToken` locks global callback state, stores the token, starts the `fscrypt` PAM service transaction, calls `Authenticate`, and maps false authentication to `ErrPassphrase`. `passphraseInput` returns a C string copy of the token on first prompt and then clears `tokenToCheck` so repeated secret prompts fail. `userInput` prompts on stdout for echo-on input.

## State and Persistence
The login token remains caller-owned; this file does not wipe it. A transient C string copy is returned to PAM and must be cleaned by the PAM conversation cleanup. Global state exists only while the lock is held.

## Dependencies and Integration Points
Uses `crypto.Key.UnsafeToCString`, PAM transaction wrappers in `pam.go`, util line input, cgo exports, and libpam. It is used by higher-level actions that need to validate login passphrases.

## Risks
Global callback state prevents concurrent PAM token checks and would be unsafe without the mutex. `UnsafeToCString` creates an unmanaged C copy, so cleanup correctness is important. PAM modules may request multiple secret prompts, which this implementation deliberately rejects.

## Test Signals
No substantive local tests; PAM package has only a trivial stub. Behavior is indirectly exercised where login protector workflows are integration-tested outside this subset.
