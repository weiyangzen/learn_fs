<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/creds/creds_test.go -->
# sources/sync-backup/git-lfs/creds/creds_test.go

## Research

This file tests credential protocol formatting and the helper-chain state machine. `TestCredsBufferFormat` asserts capability lines and multi-value `wwwauth[]` output. `TestCredsBufferProtect` verifies LF and NUL are always rejected and CR is rejected only when protocol protection is enabled. The remaining tests use fake helpers plus `credentialCacher` to cover fill success, fill errors causing helper skip, approve errors, combined fill/approve errors, reject errors, cache population, cache clearing, and all-fill-error aggregation.

The tests are pure and do not invoke real `git credential` or askpass programs. They provide strong coverage for in-memory helper composition and injection protection. Gaps include `CredentialHelperContext` URL input construction, netrc integration, multistage `continue`, actual command helper exit-code handling, and askpass prompt behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/creds/creds_test.go -->
