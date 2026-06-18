<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/config/extension_test.go -->
# sources/sync-backup/git-lfs/config/extension_test.go

## Research

This file tests `SortExtensions`. `TestSortExtensions` builds three extension entries out of map order and expects output sorted by priorities `0`, `1`, and `2` with names and command strings intact. `TestSortExtensionsDuplicatePriority` verifies that duplicate priority values return an error and no sorted result.

The tests are pure and cover the main contract. They do not cover nil maps, negative priorities from parser behavior, or how `Configuration.readGitConfig` ignores unsafe extension command keys from `.lfsconfig`. Their value is preventing nondeterministic extension ordering in clean/smudge pipelines.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/config/extension_test.go -->
