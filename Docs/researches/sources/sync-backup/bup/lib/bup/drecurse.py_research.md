# sources/sync-backup/bup/lib/bup/drecurse.py

## Purpose
`drecurse.py` is the low-level directory traversal engine for indexing and diagnostic traversal. It performs byte-path, no-follow, no-atime recursive listing with exclude and filesystem-boundary controls.

## APIs and Control Flow
`_dirlist(fd, path)` lists a directory by fd, `lstat`s entries relative to that fd, appends `/` to directory names, sorts reverse, and returns `(name, stat)` pairs. `_recursive_dirlist` filters literal and regex excludes, skips the bup repo directory, enforces `xdev` except for allowed paths, yields files immediately, descends into directories with `openat_noatime(... O_NOFOLLOW|O_DIRECTORY)`, yields children, then yields the directory path. `recursive_dirlist(paths, xdev, ...)` validates byte paths, stats each root, handles non-directories, opens directory roots, sets the starting device when xdev is enabled, and yields post-order directory entries.

## State, Dependencies, Integration, Risks, Tests
It persists nothing but reports errors through shared helper error state. Dependencies include `xstat.lstat`, compiled no-atime open helpers, `finalized`, `resolve_parent`, and regex exclude helpers. It integrates with `cmd/index.py` and `cmd/drecurse.py`. Risks include reverse sorting/post-order expectations required by index merge logic, symlink loop avoidance through no-follow flags, bytes/path formatting bugs in debug strings, permission errors, and filesystem boundary exceptions. Test signals include post-order traversal, file-vs-directory names, bup_dir exclusion, xdev skip-yield behavior, open/stat errors, exclude matching, and relative/absolute byte paths.
