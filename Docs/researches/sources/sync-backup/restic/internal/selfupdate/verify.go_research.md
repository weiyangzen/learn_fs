<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/selfupdate/verify.go -->
# sources/sync-backup/restic/internal/selfupdate/verify.go

## Purpose
Verifies detached GPG signatures for self-update metadata using an embedded public key.

## Important APIs and Control Flow
The file embeds the restic release signing key and exposes `GPGVerify(data, sig)`, which parses the keyring and signature and checks that the signature was made by a trusted embedded key. Control flow builds OpenPGP entities from the key material, verifies the signature against the supplied data, and returns `(ok,error)` instead of panicking.

## State, Persistence, Dependencies, and Integration
State is static embedded key text plus transient verification objects. It depends on OpenPGP packages and is called by `DownloadLatestStableRelease` before trusting `SHA256SUMS`.

## Risks and Test Signals
Risk is high because update authenticity depends on this path; stale/revoked keys or weakened OpenPGP dependencies would affect updates. Coverage is mostly integration through self-update flow rather than extensive unit tests in this file.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/selfupdate/verify.go -->
