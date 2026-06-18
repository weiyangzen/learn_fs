<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/config/git_fetcher_test.go -->
# sources/sync-backup/git-lfs/config/git_fetcher_test.go

## Research

This unit test verifies `GitFetcher.caseFoldKey` through public `GetAll` calls. It asserts that ordinary two-part keys are case-insensitive, while the middle component of branch and URL-scoped keys remains case-sensitive and the final key segment is case-insensitive.

The test is pure and has no persistence. It is an important regression signal because URL-scoped config such as `http.https://example.com/BIG-TEXT.git.extraheader` and branch names can be case-sensitive. Gaps include `.lfsconfig` safe-key filtering, extension parsing, duplicate warnings, remotes with dots, and `All` copy behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/config/git_fetcher_test.go -->
