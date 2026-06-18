<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/filter/filter_test.go -->
# sources/user-network-fs/rclone/fs/filter/filter_test.go

## Purpose
Comprehensive tests for filter option parsing and inclusion behavior.

## Important APIs, Types, And Control Flow
Tests cover default filters, hash-filter parsing, forbidden mixing of files-from with other filters, files-from/raw list loading, include/exclude/filter rules, directory include decisions, files-from `ListR`, min/max size and age, case-insensitive matching, regex globs, metadata include/exclude, adding directory/file rules, line reading from files/stdin with raw and non-raw modes, documentation examples, directory-filter usage detection, and context config helpers.

## State And Persistence
Uses temporary files and temporarily replaces stdin in line-reading tests. Context-local filter configs avoid mutating only global state where possible.

## Dependencies And Integration Points
Uses mock objects/filesystems, filter rule files, metadata maps, and testify. It exercises `glob.go` and `rules.go` through public filter construction.

## Risks And Test Signals
Strong behavioral coverage. Remaining risks are time-dependent age boundaries, random `@/n` hash partitions, and backend-specific filter-aware listing interactions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/filter/filter_test.go -->
