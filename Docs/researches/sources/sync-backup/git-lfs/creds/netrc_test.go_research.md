<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/creds/netrc_test.go -->
# sources/sync-backup/git-lfs/creds/netrc_test.go

## Research

This test file uses `fakeNetrc` to validate `netrcCredentialHelper.Fill`. It verifies that a host with a port is normalized before lookup, a bare host lookup works, and an unmatched host returns the sentinel `credHelperNoOp`.

The tests are pure and avoid filesystem parsing. They confirm the key integration behavior needed before the helper chain falls through to other credential sources. Remaining gaps include actual `.netrc` file discovery/parsing, Windows `_netrc`, reject/approve skip state, login-name-specific matching, malformed host:port values, and missing input keys.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/creds/netrc_test.go -->
