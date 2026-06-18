# sources/user-network-fs/rclone/lib/version/version.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/version/version.go -->
## sources/user-network-fs/rclone/lib/version/version.go

Purpose: adds, removes, and detects timestamp version suffixes in file names.

Important APIs and control flow: `splitExt` separates base and extension using `path.Ext`, with special handling so dotfiles like `.file` are treated as base with no extension. `Add(fileName, t)` formats time with `-v2006-01-02-150405.000`, replaces the millisecond dot with a dash, and inserts before extension. `Remove(fileName)` checks the end of the base for a version-length suffix, restores the millisecond dot for parsing, and returns parsed time plus filename without version; if parsing fails, it returns zero time and original filename. `Match` uses a regexp to find version-like substrings.

State, dependencies, and integration: stateless. Dependencies are `path`, `regexp`, `strings`, and `time`. It integrates with backup/versioning logic that stores old object names with timestamp suffixes.

Risks and test signals: `Match` is regex-based and accepts impossible dates such as month 99, while `Remove` requires parseable time. `Remove` targets the final version suffix before extension. Tests cover extension insertion, dotfiles, stacked versions, removal, invalid versions, and regex matching.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/version/version.go -->
