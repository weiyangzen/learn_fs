# sources/sync-backup/kopia/repo/content/sessions.go

## Purpose
Tracks active write sessions by writing encrypted session marker blobs. Session markers let repository upgrade and maintenance paths detect active writers and provide user/host/checkpoint metadata.

## Important APIs, Types, And Functions
Exports `BlobIDPrefixSession`, `SessionID`, `SessionInfo`, `SessionIDFromBlobID`, and `WriteManager.ListActiveSessions`. Internal functions include `checkClockSkewBounds`, `maybeCheckClockSkewBounds`, `generateSessionID`, `WriteManager.getOrStartSessionLocked`, `commitSession`, and `writeSessionMarkerLocked`.

## Control Flow
When a write manager starts a session, it generates a random session ID with a coarse monthly epoch suffix, fills user/host/start metadata, and writes a marker. A marker is JSON-marshaled, encrypted using `blobcrypto.Encrypt` with the session ID as suffix, then written to blob storage while optionally collecting the storage modification time. Commit deletes all marker blobs recorded in the session. Listing scans session-prefixed blobs, extracts the session ID from the blob name, decrypts each marker, decodes JSON, and keeps the latest checkpoint per session.

## State And Persistence
Session state lives both in memory on `WriteManager` (`currentSessionInfo`, `sessionMarkerBlobIDs`) and in storage as encrypted `s...` blobs. The optional clock-skew check is controlled by `KOPIA_ENABLE_CLOCK_SKEW_CHECK`; it is disabled unless the variable is present and not explicitly false.

## Dependencies And Integration Points
The file depends on `blobcrypto`, `gather`, `blob.Storage`, environment variables, JSON, and `WriteManager` fields. Upgrade-lock monitoring and repository availability checks use active session information to avoid unsafe upgrades during ongoing writes.

## Risks And Edge Cases
Clock skew detection can reject marker writes when enabled and storage timestamps differ by more than five minutes. Marker cleanup ignores already-missing blobs but returns other deletion errors. `SessionIDFromBlobID` searches dash-separated suffixes for an `s` prefix, so malformed session-prefixed blobs cause listing errors.

## Test Signals
`sessions_test.go` covers session ID uniqueness, blob ID parsing, explicit clock-skew checking, environment-gated skew checking, and marker writes with matching and skewed storage clocks.
