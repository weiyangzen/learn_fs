# sources/user-network-fs/samba/source3/modules/vfs_streams_depot.c

## Purpose

`vfs_streams_depot.c` implements named streams by storing each stream as a real file under a sidecar directory tree. By default this tree lives at `<share connectpath>/.streams`, although the `streams_depot:directory` parameter can move it elsewhere. The module exposes `FILE_NAMED_STREAMS`, maps stream paths to sidecar files based on the base file's stable file id, and supports stream stat, open, unlink, rename, and enumeration.

## Important APIs, Types, And Functions

`struct streams_depot_config_data` stores `directory`, `check_valid`, and `delete_lost` configuration. `struct streams_depot_dirnames` carries the two-level hash and hex file-id directory components. `hash_fn()` and `streams_depot_get_dirnames()` derive paths like `XX/YY/<file-id-hex>`.

Path helpers are central: `stream_rootdir()` resolves the configured root; `streams_depot_rootdir_pathref()` opens or creates it; `streams_depot_mkdir_pathref()` creates and opens pathref directories; `stream_dir_pathref()` opens or creates a base file's stream directory; and `stream_name()` normalizes a stream name to `:<name>:$DATA`, rejecting non-`$DATA` stream types. `walk_streams()` iterates sidecar entries.

VFS hooks include `streams_depot_openat()`, `streams_depot_fstatat()`, `streams_depot_stat()`, `streams_depot_lstat()`, `streams_depot_unlinkat()`, `streams_depot_rename_stream()`, `streams_depot_fstreaminfo()`, `streams_depot_fs_capabilities()`, and `streams_depot_connect()`.

## Control Flow

Non-stream operations mostly delegate directly to the next VFS module. For named streams, stat converts the requested name to a base file path, validates that the base exists, resolves its hashed sidecar directory, normalizes the stream filename, and stats the sidecar file. Open asserts an alternate-stream `fsp`, uses the already-open `base_fsp` and its stat data, creates the sidecar directory on `O_CREAT`, optionally marks the base file with `SAMBA_XATTR_MARKER`, and opens the stream file inside the sidecar directory.

When a base file is unlinked, the module computes the stream directory path from the base file id and tries to remove that directory before unlinking the base file. Stream unlink removes only the normalized sidecar stream file. Stream rename renames files within the same sidecar directory and checks destination existence when `replace_if_exists` is false. Enumeration walks the sidecar directory, stats each entry, appends `stream_struct` entries, and then calls the next `fstreaminfo` on `metadata_fsp(fsp)`.

## State And Persistence

Persistent stream bytes are ordinary files under the depot directory. Directory structure is deterministic from the base file's `file_id`, not from the pathname. If `check_valid` is enabled, the base file gets `SAMBA_XATTR_MARKER` set to `'1'` when a stream is created, and `stream_dir_valid()` later uses that marker to detect directories left behind after inode reuse. Invalid stream directories are either recursively removed when `delete_lost` is true or renamed to a `lost-<random>` name.

## Dependencies And Integration Points

The module depends on Samba pathref helpers, VFS file-id creation, xattr functions, directory iteration helpers, recursive directory removal, and standard VFS open/stat/rename/unlink operations. It is registered as `streams_depot` and built from `source3/modules/wscript_build`. Selftest references include stream depot torture shares such as `vfs_fruit_stream_depot`, `vfs_wo_fruit_stream_depot`, and `external_streams_depot`.

## Risks And Edge Cases

The file-id based path scheme is vulnerable to orphaned stream directories if files are deleted outside Samba; the marker mechanism mitigates this only on filesystems with usable xattrs and only after Samba has created a stream. Base-file unlink removes the stream directory before unlinking the base, but it ignores sidecar removal failure, so orphaned streams can remain. The stream directory root can be outside the share, so permission, backup, and cleanup policy need explicit attention. The code rejects unsupported stream types and unsupported open resolution flags, which is correct but observable to clients. Cross-filesystem or externally modified depot directories can produce stale or hidden stream state.

## Test Signals

Test coverage should create, open, stat, rename, enumerate, and delete alternate data streams; verify sidecar cleanup on base-file delete; verify invalid-directory rename/delete behavior under inode reuse simulations; test configured external depot directories; and confirm `FILE_NAMED_STREAMS` is advertised. Existing Samba selftest/torture references for streams depot and fruit integration are strong signals for this module.
