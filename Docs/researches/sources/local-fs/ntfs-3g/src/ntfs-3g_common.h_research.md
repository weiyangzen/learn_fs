# File Research: sources/local-fs/ntfs-3g/src/ntfs-3g_common.h

## Role

`ntfs-3g_common.h` declares shared structures, enums, macros, globals, and function prototypes used by `ntfs-3g` and `lowntfs-3g`. It is the contract for common option parsing, stream mode selection, FUSE context state, xattr helpers, and reparse plugin operations.

## Command Option State

`struct ntfs_options` stores command-line state before it is converted into a mounted context:

- `mnt_point`: mount point path.
- `options`: raw comma-separated mount options.
- `device`: canonicalized device path.
- `arg_device`: original device argument.

## Stream Interface Modes

`ntfs_fuse_streams_interface` defines how NTFS alternate data streams are exposed:

- `NF_STREAMS_INTERFACE_NONE`: no named stream access.
- `NF_STREAMS_INTERFACE_XATTR`: named streams mapped to xattrs.
- `NF_STREAMS_INTERFACE_OPENXATTR`: xattr mapping without limiting to `user.` namespace.
- `NF_STREAMS_INTERFACE_WINDOWS`: Windows-style `file:stream` paths.

These modes drive path parsing, xattr namespace handling, and platform defaults.

## Mount Option Definitions

`struct DEFOPTION` describes a recognized mount option:

- option name
- option enum type
- validation/behavior flags

The option enum covers all NTFS-3G-specific mount options handled by `parse_mount_options()`, including access mode, atime mode, permission/security settings, masks, ownership, visibility, filename policy, compression, recovery, streams, debug, user mappings, xattr mappings, EFS raw mode, POSIX link count mode, special file mode, help, and version.

Option flags include:

- bogus/no-value options
- string-valued options
- octal-valued options
- decimal-valued options
- append-to-FUSE options
- unsupported options
- optional-valued options

## Context State

`ntfs_fuse_context_t` is the central runtime context shared by FUSE callbacks.

It contains:

- Mounted `ntfs_volume *vol`.
- Default uid/gid.
- File and directory masks.
- Stream interface mode.
- Atime policy and delayed mtime interval.
- Read-only/read-write flags.
- Visibility and naming flags.
- Compression, ACL, silent, recovery, hibernation, sync, big-write, debug, no-detach, block-device, mounted, and POSIX nlink flags.
- Special file mode for Interix or WSL handling.
- Optional EFS raw and xattr mapping path state.
- FUSE channel pointer.
- NTFS security inheritance and secure flags.
- One-shot logged error flags.
- User mapping path and absolute mount point.
- Reparse plugin list when plugins are enabled.
- Permissions cache and current security context.
- `open_files` for low-level FUSE usage.
- `latest_ghost`, also for low-level or cleanup tracking.

## Plugin State

When plugins are enabled, `plugin_list_t` records:

- next plugin node
- dynamic library handle
- plugin operations vector
- selected reparse tag

The header declares plugin lifecycle functions:

- `register_reparse_plugin()`
- `select_reparse_plugin()`
- `close_reparse_plugins()`

## Shared Globals And Macros

- `EXEC_NAME` is extern so shared code can log using the current executable name.
- `FUSE_TYPE` expands to `"integrated FUSE"` or `"external FUSE"` depending on build configuration.
- xattr namespace constants and prefix lengths are exported for xattr code.

## Shared Function Prototypes

The header declares:

- `ntfs_strappend()`
- `ntfs_strinsert()`
- `parse_mount_options()`
- `ntfs_parse_options()`
- `ntfs_fuse_listxattr_common()`
- `user_xattrs_allowed()`

These are implemented in `ntfs-3g_common.c` and used by the main FUSE frontends.

## Important Dependencies

- Includes `inode.h`, which brings in NTFS inode/volume types used throughout the context.
- Relies on plugin operation types and reparse types being available through the broader NTFS-3G include graph.
- Uses build-time feature macros such as `FUSE_INTERNAL`, `HAVE_SETXATTR`, `XATTR_MAPPINGS`, and `DISABLE_PLUGINS`.

## Notable Limitations And Risk Areas

- `ntfs_fuse_context_t` is broad and mutable; most major subsystems share it, so option parsing, mount setup, and callbacks are tightly coupled.
- Many fields are conditionally compiled, making ABI and behavior dependent on build configuration.
- The stream interface enum affects both path syntax and xattr behavior, so mode changes have broad surface area.
- `open_files` is only defined for `lowntfs-3g`, but remains in the shared context.
