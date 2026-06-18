# sources/sync-backup/restic/internal/filter/include.go

Purpose: Defines include-pattern configuration and match functions used by restore/filter flows. `IncludePatternOptions` wires CLI flags for case-sensitive and case-insensitive include patterns and include-file variants.

Important APIs: `IncludeByNameFunc`, `IncludePatternOptions.Add`, `Empty`, `CollectPatterns`, `IncludeByPattern`, and `IncludeByInsensitivePattern`. `CollectPatterns` reads pattern files, validates all user patterns with `ValidatePatterns`, and returns an ordered slice of matchers.

Control flow and state: Pattern state is transient and held in slices on the options struct. File-backed patterns are appended into the same in-memory include slices. `IncludeByPattern` parses once, then calls `ListWithChild` per path and returns both direct match and child-may-match. The insensitive path lowercases both patterns and candidate names.

Dependencies and integration: Depends on local filter helpers (`readPatternsFromFiles`, `ValidatePatterns`, `ParsePatterns`, `ListWithChild`), `pflag`, and restic errors. Restore code can combine returned `IncludeByNameFunc` values to prune traversal.

Risks: `warnf` is called unconditionally on `ListWithChild` errors; callers should pass a non-nil warning function. Case-insensitive matching uses Unicode/language-agnostic `strings.ToLower`, which is simple but not locale-aware. Pattern ordering appends insensitive matchers before sensitive matchers.

Test signals: `include_test.go` covers direct glob matches and case-insensitive matching for extensions and `README.md`.
