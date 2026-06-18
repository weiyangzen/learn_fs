<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/creds/netrc.go -->
# sources/sync-backup/git-lfs/creds/netrc.go

## Research

`netrc.go` provides `.netrc` credential support. `ParseNetrc` resolves `$HOME/.netrc`, falls back to `_netrc` on Windows, parses via `github.com/git-lfs/go-netrc/netrc`, and returns a `NetrcFinder`, filename, and error. `netrcCredentialHelper` implements `CredentialHelper` using a finder plus a per-host skip map.

`Fill` strips any port from the credential host, skips hosts previously rejected, and returns username/password plus protocol/host/path/source fields when a matching machine is found. `Approve` clears skip state only for credentials whose source is `netrc`; `Reject` marks the host skipped. State is process-local and mutex-protected. Integration is early in the credential helper chain before cache, askpass, and Git credential helpers. Risks include HOME absence, Windows basename differences, parse errors disabling netrc, host:port parsing failures, indexing `what["host"][0]` in `Reject`, and source-field trust. `netrc_test.go` covers host with port, host without port, and no-op on unknown host.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/creds/netrc.go -->
