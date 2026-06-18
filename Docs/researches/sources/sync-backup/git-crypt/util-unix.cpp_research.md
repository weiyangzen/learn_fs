# sources/sync-backup/git-crypt/util-unix.cpp

Purpose: Unix/POSIX implementation of platform utility functions used by git-crypt.

Important APIs/types/functions: `System_error::message`, `temp_fstream::open/close`, `mkdir_parent`, `our_exe_path`, `exit_status`, `touch_file`, `remove_file`, `init_std_streams_platform`, `create_protected_file`, `util_rename`, and `get_directory_contents`.

Control flow: temp files are created under `$TMPDIR` or `/tmp` with `mkstemp` under a restrictive umask, opened as `fstream`, immediately unlinked, and closed via RAII. `mkdir_parent` walks slash-separated prefixes and creates missing directories. `our_exe_path` resolves absolute/relative `argv0` with `realpath` where possible. Directory listing skips `.`/`..`, checks `readdir` errors, sorts results, and returns names.

State/persistence behavior: touches mtimes, removes files, creates parent directories, creates protected files with mode 0600, and renames files. Temporary spill files are unlinked after opening and disappear on close.

Dependencies/integration: uses POSIX APIs including `stat`, `mkdir`, `mkstemp`, `umask`, `utimes`, `unlink`, `open`, `rename`, `opendir/readdir`, and wait-status macros. Included by `util.cpp` on non-Windows builds.

Risks/test signals: `realpath(argv0, nullptr)` is not null-checked, so failed relative path resolution could crash. Temp file security and protected key permissions are important. Tests should cover long/missing TMPDIR, nested directory creation, directory listing sort/error handling, `touch_file` on missing files, and protected file mode.
