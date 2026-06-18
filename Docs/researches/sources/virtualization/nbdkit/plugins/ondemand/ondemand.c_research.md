# File Research: sources/virtualization/nbdkit/plugins/ondemand/ondemand.c

## Purpose
Implements the `ondemand` plugin, which lazily creates filesystem images in a directory when clients open named exports, then serves the resulting files as NBD disks.

## Main Entry Points
- `ondemand_config()` parses `command`, `size`, `dir`, `wait`, `share`, and additional shell-variable parameters.
- `ondemand_get_ready()` opens the exports directory.
- `ondemand_list_exports()` lists existing valid export files plus the default export.
- `ondemand_default_export()` canonicalizes the empty export to `default`.
- `ondemand_open()` validates the export name, opens or creates the disk file, runs the creation command if missing, applies locking, and records size.
- `run_command()` constructs a shell script with `disk`, `size`, and configured variables, then executes it with `system()`.
- `ondemand_pread()`, `ondemand_pwrite()`, `ondemand_flush()`, and `ondemand_trim()` serve file I/O.

## Internal Mechanics
The plugin keeps an opened `DIR *` for the export directory. Export names must be nonempty, not hidden, contain no slash, and fit `NAME_MAX`. Creation is serialized by `open_lock`; export listing is serialized by `exports_lock`. Unless `share=true`, open file description locks (`F_OFD_SETLK`/`F_OFD_SETLKW`) prevent concurrent client use of the same filesystem.

## Dependencies
Uses POSIX directory and file APIs, `open_memstream`, shell quoting helpers, `system`, `fdatasync`, Linux `fallocate` hole punching when available, and nbdkit plugin API v2.

## Risks and Notes
The plugin executes shell commands assembled from configuration; it relies on `shell_quote()` and variable-name validation to keep parameters safe. Locking depends on Linux OFD locks when available; on platforms without `F_OFD_SETLK`, `lock_export()` becomes a no-op. `can_multi_conn()` deliberately returns false because the locking scheme cannot distinguish connections from the same client instance. `device_size` error messages may reference `disk`, which is only populated on create paths.
