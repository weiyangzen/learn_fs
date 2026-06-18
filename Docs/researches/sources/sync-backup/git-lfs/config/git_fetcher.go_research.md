<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/config/git_fetcher.go -->
# sources/sync-backup/git-lfs/config/git_fetcher.go

## Research

`git_fetcher.go` parses Git config output into a thread-safe fetcher and extracts LFS extensions and remotes. `readGitConfig` consumes `git.ConfigurationSource` values, splits `key=value` lines, applies `.lfsconfig` safe-key policy, records ignored unsafe keys, parses `lfs.extension.<name>.<prop>`, and collects remote names including names with dots.

`GitFetcher.Get` returns the last value; `GetAll` uses Git-compatible case folding where the middle part of three-or-more-part keys remains case-sensitive; `All` returns a copy. Persistent behavior is limited to warning output on stderr for clashes or ignored unsafe keys. Dependencies include `git.ConfigurationSource`, translation, and synchronization. Integration is central to `Configuration.Git`, URL matching, credential config, remotes, and extension sorting. Risks include line parsing by first `=`, safe-key drift, ignored-key warnings leaking to stderr, remote names with complex dots, and correctness of Git key canonicalization. `git_fetcher_test.go` targets mixed-case branch and URL keys.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/config/git_fetcher.go -->
