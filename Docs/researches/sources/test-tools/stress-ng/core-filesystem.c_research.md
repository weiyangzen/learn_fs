# sources/test-tools/stress-ng/core-filesystem.c

## Purpose

This implementation is the central filesystem utility layer for stress-ng. It provides temporary path construction and cleanup, filesystem capacity and type reporting, robust file read/write wrappers, descriptor and pipe limit discovery, directory entry utilities, Linux cache-dropping and inode-flag cleanup, and small helpers used by many stressors that interact with `/proc`, `/sys`, temporary files, file descriptors, pipes, and mounted filesystems.

## Important APIs, Types, And Functions

The private `stress_fs_name_t` table maps Linux `statfs` magic values to human-readable filesystem names when `linux/magic.h` and `statfs` are available. The public API surface includes `stress_fs_temp_path_get`, `stress_fs_temp_path_check`, `stress_fs_make_filename`, `stress_fs_size_get`, `stress_fs_available_inodes_get`, `stress_fs_usage_bytes`, `stress_fs_nonblocking_set`, `stress_fs_temp_filename*`, `stress_fs_temp_dir*`, `stress_fs_file_write`, `stress_fs_file_read`, `stress_fs_discard`, `stress_fs_max_file_limit_get`, `stress_fs_file_limit_get`, `stress_fs_bad_fd_get`, `stress_fs_pipe_check`, `stress_fs_max_pipe_size_get`, `stress_fs_dirent_list_free`, `stress_fs_dirent_list_prune`, `stress_fs_read`, `stress_fs_write`, `stress_fs_fdinfo_read`, `stress_fs_extents_get`, `stress_fs_info_get`, `stress_fs_type_get`, `stress_fs_close_fds`, `stress_fs_file_rw_hint_short`, `stress_fs_chattr_flags_unset`, `stress_fs_clean_dir`, and `stress_fs_drop_caches`.

Temp-name generation is intentionally robust against small filesystem name limits: `stress_fs_temp_hash_truncate` checks `statvfs(...).f_namemax` and replaces oversized directory or file names with a base-36 encoding of a 64-bit hash derived from Jenkins and PJW hashes. `stress_fs_temp_filename` and `stress_fs_temp_dir` include program name, stressor name, PID, instance, and optional magic to isolate stressor output.

## Control Flow

Most helpers are direct wrappers around one filesystem operation with validation and fallback. Capacity functions read `statvfs` from the configured temp path. Limit probes combine `getrlimit`, `/proc/sys/fs/file-max`, `sysconf(_SC_OPEN_MAX)`, and `getdtablesize` where available. `stress_fs_max_file_rlimit` uses binary search and temporary `setrlimit` calls to discover the largest possible `RLIMIT_NOFILE`, while `stress_fs_file_limit_get` subtracts open descriptor count using `/proc/self/fd` or a fallback scan.

Directory cleanup is recursive but guarded. `stress_fs_clean_dir` computes the expected temp directory, checks access, then calls `stress_fs_clean_dir_files`. The recursive cleanup refuses null paths, symlinks, paths containing `..`, and paths outside the configured temp root. It uses `scandir` with a dot-entry filter, removes immutable/chattr flags, attempts `swapoff` for names containing `swap`, unlinks regular files and symlinks, and removes directories on unwind.

## State And Persistence Behavior

State is mostly external filesystem state. Temporary directories and files persist until the owning stressor removes them or `stress_fs_clean_dir` reclaims leftovers after abnormal termination. `stress_fs_max_pipe_size_get` caches the discovered maximum pipe size in a static variable. Filesystem type formatting uses static buffers for unknown names and return strings, so these results are not reentrant. `stress_fs_drop_caches` affects global Linux VM cache state through `/proc/sys/vm/drop_caches` after `sync`.

## Dependencies And Integration Points

The file depends on stress-ng globals and helpers such as `g_prog_name`, `stress_setting_get`, `stress_uint64_to_str`, logging functions, hash functions, sort comparison helpers, shim wrappers, and memory helpers. It integrates directly with Linux `/proc`, `/sys`, ioctls such as `FS_IOC_FIEMAP`, `FS_IOC_SETFLAGS`, `F_SET_FILE_RW_HINT`, `F_SETPIPE_SZ`, and cross-platform `statvfs`/`statfs` APIs. It is used by CPU ignition, memory management, process diagnostics, stressor temp-file setup, and option parsing for maximum file descriptors.

## Risks And Test Signals

High-risk paths are recursive cleanup, rlimit probing, and global kernel toggles. Cleanup must never escape the configured temp root or follow symlinks. Rlimit discovery temporarily changes process limits and can behave differently under containers, shells, and restricted users. Linux-only ioctls and `/proc` files must degrade gracefully. Useful test signals include temp-path accessibility failures, hashed long names on constrained filesystems, cleanup of immutable files and swap files, correct dot-entry pruning, short-read/short-write behavior, descriptor closing with `close_range`, `drop_caches` permission failures, and filesystem type strings on Linux and BSD.
