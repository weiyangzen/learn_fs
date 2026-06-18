# File Research: sources/local-fs/e2fsprogs/misc/lsattr.c

`lsattr.c` implements the `lsattr` command for listing ext-family inode attributes on files and directories.

Core behavior:
- Parses `-R`, `-V`, `-a`, `-d`, `-l`, `-v`, and `-p`.
- Uses `lstat`/`lstat64` so symbolic links are inspected without following directory loops.
- Calls `fgetflags()` and `print_flags()` from e2p support code to retrieve and display inode flags.
- Optional `-v` prints inode generation/version via `fgetversion()`.
- Optional `-p` prints project ID via `fgetproject()`.
- Optional `-l` switches to long formatting with name before flags.
- If no files are supplied, operates on `.`.

Directory traversal:
- `lsattr_args()` decides whether to list a path directly or iterate a directory.
- `lsattr_dir_proc()` builds child paths, skips dot entries unless `-a` is set, and recursively descends when `-R` is active.
- Recursion explicitly avoids descending into `.` and `..`.
- Path allocation guards against extremely large directory/name lengths before `malloc`.

Important dependencies:
- `e2p/e2p.h`: file flag/project/version helpers and flag formatting.
- `et/com_err.h`: consistent error reporting.
- `support/nls-enable.h`: translated messages.
- `../version.h`: version banner.

Research notes:
- The utility works through host filesystem ioctls/helpers rather than opening an ext filesystem image through libext2fs.
- Errors are reported per path and converted into a nonzero process exit if any top-level argument fails.
- The file is self-contained CLI glue around e2p attribute helpers and directory iteration.
