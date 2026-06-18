# sources/user-network-fs/samba/source3/modules/vfs_unityed_media.c

## Purpose

`vfs_unityed_media.c` is a Samba VFS module for Avid shared-media workflows. It makes client-specific suffixed media directories appear as unsuffixed numeric directories to each client, reducing collisions when multiple clients use `Avid MediaFiles/MXF` or `OMFI MediaFiles`. The module rewrites paths under those media roots to include a suffix derived from username, client IP, or hostname.

## Important APIs, Types, And Functions

`enum um_clientid` selects suffix identity: `user`, `ip`, or `hostname`. `struct um_config_data` stores that choice. `um_dirinfo_struct` wraps a real `DIR *` plus original path, client path, media-root flag, and current client subdirectory name.

Path helpers include `get_digit_group()`, which extracts the first numeric group from a path; `alloc_append_client_suffix()`, which appends `_<clientid>.<number>`; `is_apple_double()`, `starts_with_media_dir()`, `is_in_media_dir()`, and `is_in_media_files()`, which recognize Avid/OMFI media roots and levels; `alloc_get_client_path()` and `alloc_get_client_smb_fname()`, which transform visible paths to client-specific physical paths; and `alloc_set_client_dirinfo()` helpers for directory listing state.

The VFS table wraps connect, fstatvfs, directory open/read/rewind/close, mkdir, open, create_file, rename, stat/lstat/fstat, unlink, lchown, chdir, symlink/readlink, link, mknod, and realpath. Async xattrat hooks are explicitly not implemented.

## Control Flow

Connect reads `unityed_media:clientid`, defaulting to username, and stores config. Most VFS calls first check whether the target path is under `Avid MediaFiles/MXF` or `OMFI MediaFiles`; outside those roots they delegate unchanged. Inside media roots, paths are copied and the relevant numeric component is suffixed with the selected client identity and the extracted number. Operations that receive `dirfsp` build full paths first, then call the next VFS operation from `cwd_fsp` with rewritten names when needed.

Directory listing wraps the real `DIR *` in `um_dirinfo_struct`. `um_readdir()` strips this client's suffix from matching directory names before returning entries and can skip or expose other clients' suffixed directories depending on branch behavior. AppleDouble `._` names are handled by applying suffix logic after the prefix. Stat-style calls rewrite to the physical client path, delegate, and copy stat data back to the visible filename.

## State And Persistence

Persistent state is the on-disk naming scheme: client-specific media directories such as numeric Avid directories with appended `_<client>.<number>`. The module does not store an index. Per-directory iteration state is heap allocated in `um_fdopendir()` and freed in `um_closedir()`. Per-share config is stored on the VFS handle.

## Dependencies And Integration Points

The module depends on Samba VFS pathname helpers, `get_current_username()`, `get_remote_machine_name()`, remote socket address helpers, `smb_strtoul()`, talloc string builders, and standard VFS chaining. It registers a custom debug class `unityed_media`, is built as `vfs_unityed_media`, and is listed among default shared modules in `source3/wscript`.

## Risks And Edge Cases

This module is intentionally domain-specific and can surprise general-purpose filesystem users. The numeric-group parser uses the first digit group in a path, so unexpected digits elsewhere can influence suffixing. Several comments mark FIXME areas around stat correctness for database files and directory-state behavior. Directory listing mutates `dirent->d_name` in place, which depends on the returned buffer being writable and long enough for truncation semantics. Path rewriting is string-based and must stay aligned with Samba's path normalization, AppleDouble handling, and relative path forms like `./OMFI MediaFiles`. Cross-client visibility rules are controlled by branch constants in code rather than explicit configuration.

## Test Signals

Tests should exercise username/IP/hostname suffix modes; path rewrites for `Avid MediaFiles/MXF/<number>` and `OMFI MediaFiles`; AppleDouble names; mkdir/open/create/rename/stat/unlink/link/symlink/readlink under and outside media roots; directory listing suffix stripping; and relative `./` path inputs. Avid workflow integration tests should verify that each client sees its own numeric media directories while physical storage remains suffixed.
