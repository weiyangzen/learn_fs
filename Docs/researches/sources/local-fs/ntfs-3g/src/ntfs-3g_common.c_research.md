# File Research: sources/local-fs/ntfs-3g/src/ntfs-3g_common.c

## Role

`ntfs-3g_common.c` contains shared support code for `ntfs-3g` and `lowntfs-3g`. Its main responsibilities are mount option parsing, FUSE option string construction, common command-line parsing, xattr listing helpers, user-xattr eligibility checks, and reparse plugin registration/loading/closing.

## Shared Constants

The file defines xattr namespace strings and lengths:

- `xattr_ntfs_3g = "ntfs-3g."`
- `user.`
- `system.`
- `security.`
- `trusted.`

It also defines:

- `nf_ns_alt_xattr_efsinfo = "user.ntfs.efsinfo"` for encrypted files when xattr mappings are unavailable.
- Default FUSE options `allow_other,nonempty,`.

## Option Table

`optionlist[]` is the recognized NTFS-3G mount option table. Each option has a name, enum type, and validation flags.

Major options include:

- access mode: `ro`, `rw`, `fake_rw`
- atime policy: `noatime`, `atime`, `relatime`
- delayed mtime: `delay_mtime`
- permissions/security: `default_permissions`, `permissions`, `acl`, `umask`, `fmask`, `dmask`, `uid`, `gid`, `inherit`, `addsecurids`, `staticgrps`, `usermapping`
- visibility/name behavior: `show_sys_files`, `hide_hid_files`, `hide_dot_files`, `windows_names`, `ignore_case`
- data behavior: `compression`, `nocompression`, `recover`, `norecover`, `remove_hiberfile`, `sync`, `big_writes`, `efs_raw`
- encoding/platform: `locale`, `nfconv`, `nonfconv`
- stream/xattr behavior: `streams_interface`, `user_xattr`, `xattrmapping`
- process/mount behavior: `debug`, `no_detach`, `noauto`, `remount`, `blksize`
- special file mode: `special_files`
- help/version options rejected at mount-option level

Flags enforce no value, string value, octal value, decimal value, optional value, pass-through append, or unsupported status.

## String Option Helpers

`ntfs_strappend()` appends to dynamically allocated option strings with a hard input-size guard of 8192 bytes per current/appended string. It uses `realloc()` and reports overflow or allocation failure.

`ntfs_strappend_escaped()` escapes backslashes and commas for FUSE versions where the runtime FUSE library is new enough to require it, then delegates to `ntfs_strappend()`.

`ntfs_strinsert()` inserts an option before `,fsname=` when present. This keeps `fsname` last because Solaris device names may contain commas. If no `fsname` is found, it appends.

## Mount Option Parsing

`parse_mount_options()` takes parsed high-level options and fills `ntfs_fuse_context_t`, returning a FUSE option string.

Key behavior:

- Initializes security flags and EFS/compression defaults.
- Splits the raw `-o` string on commas and `=`.
- Recognized NTFS-3G options update `ctx`.
- Unknown options are treated as FUSE options and passed through.
- Options marked `FLGOPT_APPEND`, such as `ro` and `sync`, are also added to the FUSE option string.
- `no_def_opts` suppresses default FUSE options and cancels default silent mode.
- `default_permissions` and `permissions` can append `default_permissions`.
- `acl` sets security ACL intent when compiled with POSIX ACL support.
- `umask`, `fmask`, `dmask`, `uid`, and `gid` set default ownership/masks and mark security as wanted.
- `ignore_case` is accepted only for low-level FUSE mode.
- `streams_interface` accepts `none`, `xattr`, `openxattr`, and, for regular `ntfs-3g`, `windows`.
- `user_xattr` maps to `openxattr` on macOS and `xattr` elsewhere.
- `remount` is explicitly unsupported.
- `blksize` is ignored with a warning because NTFS-3G computes it later.
- `special_files` accepts `interix` or `wsl`.
- Atime options are mutually represented by adding one of `relatime`, `atime`, or `noatime`.
- `fsname=<device>` is always appended last, with escaping when needed.
- Read-only mode clears add-security-ID behavior, disables hiberfile removal, and clears explicit rw.

On error, the partially built option string is freed and `NULL` is returned.

## Program Option Parsing

`ntfs_parse_options()` parses the command-line interface shared by `ntfs-3g` variants:

- `-o`, `--options`: append comma-separated mount options.
- `-h`, `--help`: call the supplied usage function and exit with status `9`.
- `-n`, `--no-mtab`: accepted as a no-op for automount compatibility.
- `-s`: accepted as a no-op for sloppy automount compatibility.
- `-v`, `--verbose`: accepted but unused because `mount(8)` may pass it.
- `-V`, `--version`: prints version, FUSE type, and FUSE version, then exits.
- First non-option argument is canonicalized as the device with `ntfs_realpath_canonicalize()`.
- Second non-option argument is the mount point.
- Extra non-option arguments, missing device, or missing mount point are rejected.

## Xattr Listing Helper

When `HAVE_SETXATTR` is enabled, `ntfs_fuse_listxattr_common()` lists NTFS named data streams as extended attributes.

Behavior:

- Iterates `AT_DATA` attributes from an existing search context.
- Skips unnamed data.
- Converts NTFS Unicode stream names to multibyte strings.
- In prefixing mode, hides internal `ntfs-3g.*` attributes and returns user streams as `user.<stream>`.
- In open namespace mode, returns names as stored.
- Checks output buffer size and returns `-ERANGE` if insufficient.
- With `XATTR_MAPPINGS`, appends mapped system attributes when accepted.
- Without mappings, appends `user.ntfs.efsinfo` for encrypted files in EFS raw mode.

The source contains a TODO noting that mapped system xattr listing should only return xattrs that are actually set, which is more complex for object IDs and DOS names.

## Reparse Plugin Registry

When plugins are enabled:

`register_reparse_plugin()`:

- Allocates a `plugin_list_t`.
- Records selected tag, operations pointer, dynamic library handle, and links it into `ctx->plugins`.

`select_reparse_plugin()`:

- Reads the inode reparse point.
- Masks the tag with `IO_REPARSE_PLUGIN_SELECT`.
- Searches already registered plugins.
- If missing, builds a plugin shared object name like `ntfs-plugin-XXXXXXXX.so`, optionally under `PLUGIN_DIR`.
- Loads it with `dlopen()`.
- Resolves `init` with `dlsym()`.
- Calls the plugin initializer with the full tag.
- Registers successful plugin operations for future calls.
- Logs plugin load failures once using `ERR_PLUGIN`.
- Returns the operations vector and optionally transfers the reparse buffer to the caller.

`close_reparse_plugins()`:

- Iterates the plugin list.
- Calls `dlclose()` for dynamically loaded plugin handles.
- Frees registry nodes.

## User Xattr Eligibility

`user_xattrs_allowed()` decides whether user xattrs may be exposed for an inode:

- Plain non-system, non-reparse files are allowed.
- The root directory is allowed even though it is metadata.
- Reparse points are allowed only if a plugin can report them as regular files or directories.
- Metadata files below `FILE_first_user` are denied.
- Interix special files are allowed only when their type is regular file or directory.

This prevents ordinary user xattrs on symlinks, FIFOs, sockets, devices, most metadata files, and unsupported reparse objects.

## Important Dependencies

- FUSE option and version APIs.
- `realpath.h` for device canonicalization.
- `security.h` and `xattrs.h` for security and xattr policy.
- `reparse.h` and `plugin.h` for plugin loading.
- `inode.h`, `dir.h`, and NTFS attribute search APIs for xattr enumeration and inode type checks.
- Optional `dlfcn.h` dynamic loading.

## Notable Limitations And Risk Areas

- Mount option parsing uses `strsep()` and direct comma splitting, so correct escaping matters for pass-through FUSE options and device names.
- The string helper guard prevents very large option strings but also imposes a fixed practical limit.
- Unknown options are passed through to FUSE, so typo behavior depends on whether the option name is known to NTFS-3G.
- Some options are accepted as no-ops for compatibility, which can hide caller assumptions.
- Dynamic plugin loading failures are collapsed to `ELIBACC` and logged once; subsequent unsupported reparse behavior depends on caller fallback.
- The xattr mapping TODO means list results may include mapped system names without fully proving the backing data exists.
