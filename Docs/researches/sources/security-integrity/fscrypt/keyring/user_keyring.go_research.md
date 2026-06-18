# sources/security-integrity/fscrypt/keyring/user_keyring.go

## Purpose
`user_keyring.go` implements the legacy Linux user-keyring path for v1 fscrypt policy keys. It creates `logon` keys containing `unix.FscryptKey` payloads and links/accesses target users' uid keyrings.

## Important APIs, Types, and Functions
Errors are `ErrAccessUserKeyring` and `ErrSessionUserKeyring`. `KeyType` is `logon`. Core functions are `userAddKey`, `userRemoveKey`, `userFindKey`, `UserKeyringID`, `userKeyringIDLookup`, `isUserKeyringInSession`, and `keyringLink`.

## Control Flow
Operations lock the current OS thread to keep thread-keyring possession stable. Adding builds a locked `FscryptKey` payload, resolves the target user keyring, then calls `unix.AddKey`. Removing searches then unlinks. `UserKeyringID` ensures non-root callers only use a user keyring linked into the session keyring when requested, while root links target keyrings into root's user keyring to keep access. `userKeyringIDLookup` temporarily changes real/effective UIDs to make `KEY_SPEC_USER_KEYRING` refer to the target UID, links it into the thread keyring, then restores UIDs.

## State and Persistence
State is in kernel user/session/thread keyrings. The function temporarily changes process UIDs and persists links in root or thread keyrings as needed. Sensitive key payloads are allocated as `crypto.Key` and wiped after `AddKey`.

## Dependencies and Integration Points
Depends on `crypto.Key`, `security.SetUids/GetUids`, Linux keyctl syscalls, `runtime.LockOSThread`, and user identity helpers. It is selected by `keyring.go` for v1 policies when filesystem keyrings are not configured or unavailable.

## Risks
UID switching and keyring possession are subtle and process-wide/thread-sensitive. Non-root behavior depends on session keyring setup; otherwise `ErrSessionUserKeyring` is returned. The legacy mechanism has weaker policy semantics than filesystem keyrings and is unsuitable for v2.

## Test Signals
`keyring_test.go` covers user keyring add/status/remove for v1 descriptors and invalid key lengths. Root/session edge cases are indirectly tested through integration conditions rather than unit mocks.
