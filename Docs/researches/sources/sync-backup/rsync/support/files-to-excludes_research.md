<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/files-to-excludes -->
# sources/sync-backup/rsync/support/files-to-excludes

Purpose: transform a list of file paths into rsync include/exclude filter rules that transfer exactly those files plus their containing directories.

Important APIs/types/functions: `main()` reads paths through `fileinput`, tracks directory prefixes in a set, and prints filter rules. Argparse accepts zero or more input files, defaulting to stdin.

Control flow: for each input line, strip whitespace and leading slashes, split by `/`, emit `+ /dir/` rules for every parent directory not already printed, emit `+ /full/path` for the file, then after all input emit `- /dir/*` for each tracked directory and a final `- /*`.

State and persistence behavior: no filesystem mutation. Output order for parent include rules follows input discovery; directory exclude rules are sorted.

Dependencies and integration points: consumed by rsync as `--exclude-from=FILE` or merged filter rules. It is especially useful when copying sparse file lists while keeping delete behavior controlled.

Risks: blank lines become `+ /` because the code tests the split list rather than the stripped line; callers should filter empty input. Paths are treated as text and not shell-escaped. Directory names with repeated slashes are partially skipped only for empty components in parent traversal.

Test signals: fixture lists should validate parent includes, final excludes, duplicate suppression, absolute path normalization, and behavior with blank or malformed lines.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/files-to-excludes -->
