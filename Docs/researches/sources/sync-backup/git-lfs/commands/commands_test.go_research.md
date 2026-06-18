<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/commands_test.go -->
# sources/sync-backup/git-lfs/commands/commands_test.go

Purpose: unit tests for shared command helpers, currently include/exclude path selection and special migrate ref exclusion.

Important APIs/types/functions: `testcfg`, `TestDetermineIncludeExcludePathsReturnsCleanedPaths`, `TestDetermineIncludeExcludePathsReturnsEmptyPaths`, `TestDetermineIncludeExcludePathsReturnsDefaultsWhenAbsent`, `TestDetermineIncludeExcludePathsReturnsNothingWhenAbsent`, and `TestSpecialGitRefsExclusion`.

Control flow: constructs a config with default `lfs.fetchinclude` and `lfs.fetchexclude`, calls `determineIncludeExcludePaths` with explicit, empty, nil/useFetchOptions true, and nil/useFetchOptions false cases, and asserts expected slices. Special ref tests assert stash/notes/bisect/replace are excluded and a normal-ish ref is not.

State and persistence behavior: in-memory only; no filesystem or Git state.

Dependencies/integration points: uses `config.NewFrom` and `testify/assert`. It covers behavior consumed by fetch/clone/pull/ls-files/migrate filters and migrate `--everything`.

Risks and test signals: test coverage is narrow relative to `commands.go`; it does not cover path filter cache config, setup, panic logging, hook helpers, or the apparent caret exclusion bug in migrate arg parsing. Signal is fast regression coverage for default-vs-explicit include/exclude semantics and special ref namespace filtering.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/commands_test.go -->
