# File Research: sources/os/plan9/9front/sys/src/cmd/ip/cifsd/dir.c

Implements case-aware directory lookup, stat, read, and small directory-cache support for `cifsd`.

Key points:
- `xdirdup` deep-copies Plan 9 `Dir` arrays and embedded string fields into one allocation.
- `xdirread` returns a deep copy of directory entries from `xdirread0`.
- `xdirstat` first tries direct `dirstat`; if it fails, it splits path and scans the parent directory with the configured name comparator to find case-insensitive/canonical names.
- Maintains a small linked cache `xdirlist` of up to 8 directory listings keyed by path/qid.
- Cache entries are validated by comparing current `dirstat` qid against cached qid.
- If a cached path has canonical capitalization, callers may have their path replaced with the cached/canonical path.
- `xdirflush` invalidates cached entries for a directory affected by a path mutation.

Dependencies and interactions:
- Uses `splitpath`, `conspath`, and name comparison callbacks (`strcmp` or `cistrcmp`).
- Called by file creation/open and find code.

Research relevance:
- Provides CIFS case-insensitive path semantics over Plan 9 filesystem APIs.
