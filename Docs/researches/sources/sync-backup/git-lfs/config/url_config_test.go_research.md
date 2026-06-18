<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/config/url_config_test.go -->
# sources/sync-backup/git-lfs/config/url_config_test.go

## Research

This test file verifies URL-scoped config selection. It builds a synthetic environment with root, host, user, path, port, `.git`, HTTP, SSH, and wildcard host keys, then checks both `Get` and `GetAll` behavior for representative URLs.

The test signal is strong for Git-compatible matching precedence: host/path-specific values override root config, username-specific values override host-only when paths tie, explicit ports matter, default ports match, `.git/info/lfs` can match a repository path without `.git`, and malformed prefix/key patterns are ignored. Gaps include invalid raw URLs, multiple wildcard specificity cases, credential-specific skip/protect booleans, and `Bool` conversion.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/config/url_config_test.go -->
