<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/filepathfilter/filepathfilter.go -->
# sources/sync-backup/git-lfs/filepathfilter/filepathfilter.go

## Research

`filepathfilter.go` implements include/exclude path filtering for Git LFS fetch and attribute behavior. `Pattern` abstracts matchers; `Filter` stores include/exclude patterns, a default value, and optional LRU cache; `PatternType` distinguishes GitIgnore and GitAttributes semantics. Options configure default value and cache.

`New` converts raw patterns to `wildmatch.Wildmatch`; `Allows` returns true for nil filters, consults cache, then applies include-first/exclude-second logic. If include patterns exist and none match, the file is rejected. If default is false and no include matched, excludes are skipped. `NewPattern` configures wildmatch flags and optional case folding from `core.ignorecase`. State includes slices of patterns and a mutex-protected groupcache LRU. Dependencies are `git-lfs/wildmatch`, `groupcache/lru`, config-like environment, and tracer logging. Risks include cache size semantics, path separator normalization, GitIgnore vs GitAttributes behavior differences, nil environment, and cached results if config/patterns change externally. Tests cover many pattern and filter reporting cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/filepathfilter/filepathfilter.go -->
