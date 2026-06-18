<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/uploader_test.go -->
# sources/sync-backup/git-lfs/commands/uploader_test.go

## Research

This test file validates the small but security-relevant `supportsLockingAPI` helper from `uploader.go`. `LockingSupportTestCase` wraps a URL and expected result, and `TestSupportedLockingHosts` exercises HTTPS and SSH GitHub URLs with root paths, `/info/lfs` suffixes, and SSH usernames.

The test signal is that only `https://github.com/...` and `ssh://github.com/...` match the known locking support list; `http://github.com/...` is rejected. It indirectly confirms that `url.URL.Hostname()` ignores usernames and that path-prefix matching accepts both repository root URLs and batch API URLs. The file has no persistence or external I/O. Risks left uncovered include malformed URLs, ports, enterprise GitHub hostnames, host case normalization, trailing slash behavior, and lock-verification config writes in `disableFor`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/uploader_test.go -->
