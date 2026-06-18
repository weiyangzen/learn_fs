# sources/sync-backup/git-lfs/git/gitattr/files.go

Purpose: discovers repository, user, system, and working-tree attribute files and extracts patterns that are relevant to Git LFS tracking or locking. It can also build a `filepathfilter.Filter` from `filter=lfs` patterns.

Important APIs/types/functions: `AttributePath`, `AttributeSource`, `GetUserAttributePaths`, `GetUserAttributeFilePath`, `GetRepoAttributeFilePath`, `GetSystemAttributePaths`, `GetSystemAttributeFilePath`, `GetAttributePaths`, `AttrPathsFromReader`, `GetAttributeFilter`, and `findAttributeFiles`.

Control flow: global/system paths are resolved through Git config or `git var GIT_ATTR_SYSTEM` for Git 2.42+, repo attributes come from `$GIT_DIR/info/attributes`, and working-tree `.gitattributes` files are found through `git ls-files`. Each file is parsed, macro-expanded, filtered for `filter=lfs` and `lockable`, path-prefixed relative to the attribute file directory, and appended with source metadata.

State/persistence behavior: reads config and files only. The `MacroProcessor` is stateful across files so macros from higher-precedence sources can be reused where Git permits. `AttributeSource.LineEnding` records parsed EOL style.

Dependencies/integration: integrates with `git.NewLsFiles`, config path expansion, Git version checks, `filepathfilter`, and `Tree` scanning. Attribute-file ordering is sorted by path length descending to respect more-specific precedence when iterating.

Risks/test signals: file discovery depends on Git subprocess success and version behavior. Missing or unreadable attribute files are silently skipped in some paths, which is pragmatic but can hide configuration problems. Direct tests for this file are indirect through tree and scanner tests.
