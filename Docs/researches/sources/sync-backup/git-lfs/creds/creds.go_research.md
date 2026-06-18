<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/creds/creds.go -->
# sources/sync-backup/git-lfs/creds/creds.go

## Research

`creds.go` implements Git LFS credential handling. It defines `CredentialHelper`, `CredentialHelperWrapper`, the multi-value `Creds` map, `CredentialHelperContext`, askpass integration, `commandCredentialHelper` for `git credential`, an in-memory `credentialCacher`, a chained `CredentialHelpers`, `NullCreds`, and `FirstEntryForKey`.

Control flow starts with `NewCredentialHelperContext`, which configures netrc, askpass, cache, URL config, and command helper. `GetCredentialHelper` builds Git credential input from URL, `credential.usehttppath`, auth headers, and state fields, then composes helpers. `FillCreds` errors if no helper yields credentials. `Creds.buffer` emits Git credential protocol data with capability lines and rejects LF, NUL, and optionally CR injection. `commandCredentialHelper.exec` shells out to `git credential fill|approve|reject`; the helper chain skips helpers that error and clears cached approvals on downstream approve failure. Persistent behavior includes subprocess calls, in-memory credential cache, and helper skip state. Dependencies include URL config, netrc, subprocess, path translation, translation, and tracer logging. Risks are credential protocol injection, prompt suppression semantics, skipped helper lifetime, cache key granularity, multistage credentials, stderr pass-through, and askpass command trust. `creds_test.go` covers protocol formatting/protection and helper chain/cache error behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/creds/creds.go -->
