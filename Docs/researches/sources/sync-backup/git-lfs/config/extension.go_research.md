<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/config/extension.go -->
# sources/sync-backup/git-lfs/config/extension.go

## Research

`extension.go` models configured Git LFS clean/smudge extensions. `Extension` stores `Name`, `Clean`, `Smudge`, and integer `Priority`. `SortExtensions` converts a map of extensions into an ascending-priority slice and rejects duplicate priorities.

There is no persistent state; the function builds local maps/slices and returns an error translated through `tr` for collisions. Integration is through `Configuration.SortedExtensions()` after `readGitConfig` parses `lfs.extension.<name>.*` keys. The main risk is that the temporary `map[int]Extension` makes priority unique by design, so two extensions cannot share a priority; this is tested and may be stricter than some users expect. Test coverage in `extension_test.go` checks deterministic ordering and duplicate-priority rejection.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/config/extension.go -->
