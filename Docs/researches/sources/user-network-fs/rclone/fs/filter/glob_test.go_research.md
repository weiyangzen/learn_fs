<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/filter/glob_test.go -->
# sources/user-network-fs/rclone/fs/filter/glob_test.go

## Purpose
Table-driven coverage for glob-to-regexp and glob-to-directory-glob conversion.

## Important APIs, Types, And Control Flow
Tests compare exact regexp strings for string mode with/without anchors and ignore-case, path mode, invalid star/bracket/brace/regexp cases, escaped metacharacters, and raw regexp blocks. `TestGlobToDirGlobs` validates directory-pruning globs for absolute, relative, slash-squashed, brace, and `**` patterns.

## State And Persistence
No state beyond compiled regexps.

## Dependencies And Integration Points
Directly tests helpers used by filters.

## Risks And Test Signals
Strong syntax regression signal. It asserts regexp strings, so intentional parser representation changes require test updates even if matching semantics remain equivalent.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/filter/glob_test.go -->
