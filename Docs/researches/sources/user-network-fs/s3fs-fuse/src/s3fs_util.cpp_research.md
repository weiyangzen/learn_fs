# sources/user-network-fs/s3fs-fuse/src/s3fs_util.cpp

Purpose: implements miscellaneous utilities for path prefixing, sysconf-derived buffer sizing, UID/GID lookups, safe basename/dirname wrappers, recursive directory creation/deletion, directory permission checks, launch logging, `fclose` wrapping, and sensitive-string masking.

Important APIs and functions: `get_realpath`, `init_sysconf_vars`, `get_username`, `is_uid_include_group`, `mydirname`, `mybasename`, `mkdirp`, `get_exist_directory_path`, `check_exist_dir_permission`, `delete_files_in_dir`, `print_launch_message`, `s3fs_fclose`, and `mask_sensitive_string`.

Control flow: startup should call `init_sysconf_vars` before UID/GID helpers. Path helpers are used by request code to combine `mount_prefix` and object paths and to safely call libc `dirname`/`basename` under a mutex. Permission helpers use `stat`, `get[e]uid`, and group membership to decide cache/directory usability. Launch logging builds a masked command line unless insecure logging is enabled, then logs TLS-warning messages based on curl settings.

State and persistence: global `mount_prefix` and static max buffer sizes are process state. Filesystem side effects include directory creation and recursive deletion. Launch messages persist only through logging.

Dependencies and integration points: depends on libc/POSIX filesystem and passwd/group APIs, `s3fs_logger`, `string_util`, `s3fs_help`, and `S3fsCurl` TLS settings. `scope_guard` from the header is used for `closedir`.

Risks: `mkdirp` builds relative components by appending `component + "/"`, so absolute path handling and empty components need coverage. Recursive deletion is powerful and should only be called with trusted cache directories. `get_username` depends on prior `init_sysconf_vars`; missing initialization may produce zero-size/undefined behavior. `check_exist_dir_permission` requires full `rwx`, which may be stricter than some use cases.

Test signals: absolute/relative/trailing-slash tests for path helpers and `mkdirp`, passwd/group lookup tests including missing users/groups, permission matrix tests for owner/group/other directories, recursive deletion tests with files/subdirs and failure injection, and launch-message masking/TLS-warning tests.
