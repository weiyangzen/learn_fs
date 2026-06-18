<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/filepathfilter/filepathfilter_test.go -->
# sources/sync-backup/git-lfs/filepathfilter/filepathfilter_test.go

## Research

This test file validates path matching behavior through `NewPattern` and `Filter` accessors. It covers wildcards, filename-only matches in subfolders, directory-specific matches, absolute/rooted patterns, directory suffix behavior differences between GitAttributes and GitIgnore, dot/path cases, and reporting of include/exclude pattern strings.

The tests are pure and heavily exercise the external wildmatch integration. They are important because LFS include/exclude behavior controls which objects are fetched or skipped. Remaining gaps include `Filter.Allows` include/exclude combinations beyond reporting, cache behavior, `DefaultValue(false)`, `core.ignorecase`, and Windows path separator cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/filepathfilter/filepathfilter_test.go -->
