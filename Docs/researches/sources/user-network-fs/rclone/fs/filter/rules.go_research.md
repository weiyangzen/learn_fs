<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/filter/rules.go -->
# sources/user-network-fs/rclone/fs/filter/rules.go

## Purpose
Parses and evaluates ordered include/exclude rule lists for paths and metadata.

## Important APIs, Types, And Control Flow
`RulesOpt` stores CLI/config lists and rule files. `rule` wraps include bool plus regexp and formats as `+/- regexp`. `rules.add` deduplicates by formatted rule, `include` returns the first matching rule or true, and `includeMany` applies ordered rules across many strings. `forEachLine` reads files or stdin, optionally trimming comments/blank lines. `addRule` parses `+ glob`, `- glob`, and `!` clear. `parseRules` applies include/include-from, exclude/exclude-from, filter/filter-from, logs mixed include/exclude warning, and adds implicit `- /**` after includes.

## State And Persistence
Rules are in-memory slices plus a dedup map. Rule files/stdin are read but not written.

## Dependencies And Integration Points
Used by `Filter.NewFilter` for file and metadata rules. Depends on glob conversion and `fs.CheckClose` for file close errors.

## Risks And Test Signals
Rule order is user-visible. Include plus exclude option ordering is intentionally warned as indeterminate. Tests in `filter_test.go` exercise parsing, line reading, dedup, clear, and inclusion semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/filter/rules.go -->
