<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/at_fdcwd-pathmax.c -->
## sources/test-tools/strace/tests/at_fdcwd-pathmax.c

Purpose: Tests `AT_FDCWD` path annotation behavior when current working directory paths approach or exceed `PATH_MAX`.

Important APIs/types/functions: Uses `create_and_enter_subdir`, `get_fd_path`, `get_dir_fd`, `mkdir`, `chdir`, `rmdir`, `syscall(__NR_openat, AT_FDCWD, ...)`, `PATH_MAX`, and `NAME_MAX`.

Control flow: Creates nested long-name directories until the cwd path exceeds `PATH_MAX`, verifies `openat(AT_FDCWD, ...)` omits resolved cwd annotation, backs up one directory and verifies annotation appears, creates an exact-boundary directory where full resolution still fails, verifies annotation omission again, then removes all directories.

State and persistence: Temporarily creates deep `pathmax_subdir` hierarchy and removes it on completion.

Dependencies and integration: Intended for `-y` or similar fd/path decoding options and depends on filesystem path length behavior.

Risks: Filesystems with different `NAME_MAX`/path constraints or cleanup interruptions can affect behavior. The test is sensitive to exact `PATH_MAX` boundary calculations.

Test signals: Expected output alternates between `AT_FDCWD` without path and `AT_FDCWD<resolved-path>` when resolution is possible.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/at_fdcwd-pathmax.c -->
