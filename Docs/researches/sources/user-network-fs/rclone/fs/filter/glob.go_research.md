<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/filter/glob.go -->
# sources/user-network-fs/rclone/fs/filter/glob.go

## Purpose
Converts rclone/rsync-style glob syntax into Go regular expressions and derives directory globs from file globs.

## Important APIs, Types, And Control Flow
`GlobPathToRegexp` enables path mode with anchors; `GlobStringToRegexp` supports string mode with optional anchors and case-insensitivity. `globToRegexp` parses `*`, `**`, `?`, character classes, `{a,b}` alternation, raw `{{regexp}}`, backslashes, path separators, anchors, and regexp metacharacter escaping while detecting mismatched/nested constructs. `globToDirGlobs` returns possible directory globs unless the expression is too hard, in which case it logs and scans all directories.

## State And Persistence
Pure parsing plus logging for too-hard directory derivation. No persistent state.

## Dependencies And Integration Points
Used by filter rule compilation and directory-pruning optimization. Depends on regexp and fs logging.

## Risks And Test Signals
Subtle syntax compatibility risk around braces, raw regexps, and path-mode `**`. Tests cover many accepted and rejected patterns plus directory glob derivation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/filter/glob.go -->
