# sources/sync-backup/git-crypt/util-win32.cpp

Purpose: Windows implementation of platform utility functions used by git-crypt.

Important APIs/types/functions: `System_error::message`, `temp_fstream::open/close`, `mkdir_parent`, `our_exe_path`, `exit_status`, `touch_file`, `remove_file`, `init_std_streams_platform`, `create_protected_file`, `util_rename`, and `get_directory_contents`.

Control flow: error messages use `FormatMessageA`; temp files use `GetTempPath` and `GetTempFileName`, are opened as `fstream`, and deleted on close. `mkdir_parent` creates missing slash-separated prefixes. `our_exe_path` grows a buffer until `GetModuleFileNameA` fits. `touch_file` opens the file for write attributes and sets the last write time. Directory listing uses `FindFirstFileA`/`FindNextFileA`.

State/persistence behavior: sets stdin/stdout to binary mode, touches/removes/renames files, creates directories, and deletes temp files. `create_protected_file` is currently a TODO no-op, so protected key file permissions are not enforced on Windows by this layer.

Dependencies/integration: uses Win32 APIs, MSVCRT `_setmode`, and `unlink`/`rename`. Included by `util.cpp` on Windows builds.

Risks/test signals: the no-op `create_protected_file` is a security gap relative to Unix permissions. Directory listing is not sorted, unlike Unix, which can affect deterministic behavior. Tests should cover binary stdin/stdout, temp file cleanup, rename-over-existing behavior, missing file touch/remove, directory iteration, and key file ACL expectations.
