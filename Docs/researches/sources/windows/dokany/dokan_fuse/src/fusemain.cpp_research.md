# File Research: sources/windows/dokany/dokan_fuse/src/fusemain.cpp

## Role

Implements the Dokan-to-FUSE compatibility bridge for `dokan_fuse`. It translates Dokan callback semantics, Windows paths, sharing, locking, and file metadata into FUSE operation callbacks.

## Main Components

- Thread-local FUSE context stack:
  - `cur_impl_chain_link`
  - `impl_chain_guard`
  - `fuse_get_context`
- `impl_fuse_context`:
  - Wraps `fuse_operations`.
  - Runs `init`/`destroy`.
  - Implements Dokan operation handlers such as create/open/read/write/flush/stat/delete/rename/lock/time/volume info.
- Directory enumeration:
  - `find_files`
  - `walk_directory`
  - `walk_directory_getdir`
  - Supports both modern `readdir` and older `getdir`.
- File/share/byte-range lock tracking:
  - `impl_file_locks`
  - `impl_file_lock`
  - `impl_file_handle`

## Behavior

The file maps Windows/Dokan operations onto FUSE callbacks:

- `create_file`:
  - Resolves UTF-16 Windows path to UTF-8 Unix-style path.
  - Uses `getattr` to decide whether to create, open, truncate, supersede, or reject.
  - Handles directories and symlinks.
- `read_file` and `write_file`:
  - Use stored `impl_file_handle` state rather than the incoming path, because opens may have followed symlinks.
  - Enforce byte-range locks before dispatch.
  - `read_file` chunks reads by `max_read_`.
  - `write_file` honors `conn_info_.max_write`.
- `cleanup`:
  - Deletes pending files/directories on cleanup when Dokan marks `DeletePending`.
- `move_file`:
  - Implements rename with optional target replacement and updates internal lock table names.
- `set_file_time`:
  - Supports `win_set_times`, `utimens`, or `utime`.
- `get_disk_free_space` and `get_volume_information`:
  - Expose FUSE `statfs` and configured volume/filesystem names.

## Important Details

- Symlink handling uses `getattr` plus `readlink`, then resolves relative symlink targets with `extract_dir_name`.
- Directory listing attempts UTF-8 conversion first, then falls back to ANSI conversion and may rename malformed entries if possible.
- `convert_flags` reduces Windows desired access to `O_RDONLY`, `O_WRONLY`, or `O_RDWR`.
- Share access is approximated in userspace by checking prior handles for the same file.
- Local byte-range lock tracking is used when FUSE `lock` is unavailable.
- `impl_file_handle::~impl_file_handle` removes the handle from the shared lock table.

## Dependencies

- Dokan callback types and `PDOKAN_FILE_INFO`.
- FUSE types and callbacks from `fusemain.h`.
- Path/time/stat conversion helpers from `utils.h`.
- Windows constants, NT status values, POSIX errno/stat conventions.

## Notes and Risks

- Several comments identify race conditions around cleanup/delete and open files.
- Share and lock semantics are approximations of Windows behavior over FUSE callbacks.
- `do_delete_directory` refuses deletion when a handle exists, unlike Unix unlink semantics.
- Symlink relative-path normalization is marked TODO and is incomplete.
- `impl_file_locks::renamed_file` has a TODO for renaming onto an existing tracked name.
