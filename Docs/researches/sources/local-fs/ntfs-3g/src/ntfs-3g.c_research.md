# File Research: sources/local-fs/ntfs-3g/src/ntfs-3g.c

## Role

`ntfs-3g.c` is the main high-level FUSE filesystem driver for NTFS-3G. It wires FUSE callbacks to libntfs-3g volume, inode, attribute, directory, security, xattr, ioctl, EFS, and reparse-point APIs, then owns process startup, mount setup, logging, FUSE loop execution, and teardown.

It is the regular path-based NTFS-3G frontend, distinct from `lowntfs-3g`, and exposes NTFS objects as POSIX-like files, directories, symlinks, special files, alternate data streams, extended attributes, and optional POSIX ACL-backed metadata.

## Global State And Configuration

- `opts` holds parsed command-line device, mountpoint, and mount options.
- `ctx` is the process-global `ntfs_fuse_context_t` shared by all callbacks. It carries the mounted volume, masks, uid/gid defaults, stream mode, security flags, FUSE channel, reparse plugins, EFS mode, atime policy, delayed mtime setting, and platform feature switches.
- `ntfs_sequence` is used to generate temporary names during overwrite rename emulation.
- `CLOSE_COMPRESSED`, `CLOSE_ENCRYPTED`, `CLOSE_DMTIME`, and `CLOSE_REPARSE` are bit flags stored in `fuse_file_info.fh` to defer close-time work such as compressed stream close, EFS fixup, and delayed mtime update.

## Permission Model

The file compiles different permission-checking behavior from `HPERMSCONFIG`:

- `KERNELPERMS` controls whether basic permissions are delegated to FUSE/kernel.
- `KERNELACLS` controls whether POSIX ACL checks are delegated to the kernel.
- `CACHEING` controls attribute timeout behavior.
- Security checks are performed through `SECURITY_CONTEXT`, filled by `ntfs_fuse_fill_security_context()` from `ctx`, the current FUSE uid/gid/pid, user/group mappings, and optional umask support.
- Parent directory access is explicitly checked for lookup, open, create, unlink, rename, chmod/chown, timestamp changes, and xattr operations when kernel permissions are not sufficient.
- Sticky directory semantics are approximated by checking file ownership when `S_ISVTX`-style access is requested.

## Mount And Startup Flow

1. `main()` ensures descriptors 0, 1, and 2 are open.
2. With external FUSE, setuid/setgid execution is rejected as insecure.
3. Privileges are dropped, locale/logging are initialized, and `ntfs_parse_options()` parses device, mountpoint, and `-o` options.
4. `ntfs_fuse_init()` allocates `ctx` and applies defaults:
   - current uid/gid
   - Linux default streams interface as xattr, non-Linux as none
   - relative atime
   - silent mode
   - recovery enabled
5. `parse_mount_options()` builds FUSE options and fills `ctx`.
6. The code rejects conflicting existing mounts except multiple read-only mounts.
7. It resolves an absolute mount point, records mountpoint owner for default mapping, loads/creates FUSE support on Linux if needed, and decides whether to use `fuseblk`.
8. `ntfs_open()` mounts the NTFS volume with flags derived from read-only, recovery, block-device, and hibernation-removal options.
9. Read-only fallback can insert `,ro`; explicit rw can insert `,rw`; `fuseblk` adds `blkdev,blksize=`.
10. Security mappings and optional xattr mappings are built.
11. Internal reparse plugins are registered.
12. `mount_fuse()` mounts the FUSE channel, creates the FUSE handle, and installs signal handlers.
13. `setup_logging()` daemonizes unless requested otherwise and logs volume, options, and permissions mode.
14. `fuse_loop()` runs until unmount.
15. Cleanup unmounts FUSE, closes the NTFS volume, closes plugins, frees mappings/options/context, and reports mount errors.

## Volume Opening

`ntfs_open()` maps context options to libntfs mount flags:

- `NTFS_MNT_EXCLUSIVE` unless using block-device FUSE integration.
- `NTFS_MNT_RDONLY` for read-only mounts.
- `NTFS_MNT_MAY_RDONLY` for normal read-write attempts that may fall back.
- `NTFS_MNT_RECOVER` unless disabled.
- `NTFS_MNT_IGNORE_HIBERFILE` when removing hibernation state.

After `ntfs_mount()`, it applies sync and compression policy, hides/shows system/hidden/dot files, reads free-space information from `$Bitmap`, computes free MFT records, and optionally removes `/hiberfil.sys`.

## FUSE Capability Initialization

`ntfs_init()` negotiates optional FUSE capabilities:

- macOS extended times.
- `FUSE_CAP_DONT_MASK` so the filesystem can process umask.
- `FUSE_CAP_POSIX_ACL` when kernel ACL checks are enabled.
- `FUSE_CAP_BIG_WRITES` only when requested and the volume capacity is large enough.
- `FUSE_CAP_IOCTL_DIR` when available.

## Path And Stream Handling

`ntfs_fuse_parse_path()` is central to alternate data stream handling:

- In Windows stream mode, it splits `file:stream` into base path and NTFS Unicode stream name.
- Otherwise the whole string is treated as the file path and the stream name is `AT_UNNAMED`.
- `ntfs_fuse_is_named_data_stream()` rejects colon-style named streams when Windows stream mode is active for operations where streams are not meaningful.

Named stream operations are supported for file data and xattr-backed stream modes, but are rejected for directories, symlinks, chmod/chown, bmap, many metadata operations, and special-file creation.

## Stat And Attribute Reporting

`ntfs_fuse_statfs()` reports cluster-size-backed filesystem statistics:

- block size and fragment size from NTFS cluster size
- total blocks from total clusters
- free blocks from `vol->free_clusters`
- inode counts from MFT bitmap allocation plus estimated inodes fitting in free space
- free inodes from free MFT records and free-space estimate
- max filename length as `NTFS_MAX_NAME_LEN`

`ntfs_fuse_getattr()` resolves a path and fills `struct stat`:

- Directories use index allocation size if available.
- Reparse points are delegated to plugins; unsupported reparse points are exposed as symlinks with a synthetic target string.
- Regular files use `ni->data_size` and allocated-size-derived block counts.
- EFS raw mode can round encrypted nonresident data size to include padding.
- Named streams stat their own `AT_DATA` stream.
- Interix FIFO/socket/symlink/block/char devices are detected from system-file payloads.
- WSL special reparse files can report socket, FIFO, char, or block modes.
- Ownership/mode is either mapped through NTFS security descriptors or falls back to mount uid/gid plus masks.
- NTFS timestamps are converted to platform-specific stat timestamp fields.

## Directory Operations

- `ntfs_fuse_opendir()` optionally checks permissions and delegates reparse directories to plugins.
- `ntfs_fuse_readdir()` reads normal directories through `ntfs_readdir()` and reparse directories through plugins.
- `ntfs_fuse_filler()` converts NTFS Unicode names to multibyte names, skips DOS-only names, blocks names that conflict with Windows-style named stream parsing, chooses a `d_type`-like mode from NTFS directory type hints, and uses plugins to refine reparse-point types.
- Darwin and Solaris/Illumos builds truncate too-long returned names to platform limits to avoid system-call failures.

## File I/O

`ntfs_fuse_open()`:

- Resolves the file or stream.
- Opens `AT_DATA` unless the inode is a reparse point.
- Checks parent search and requested read/write permissions when needed.
- Delegates reparse opens to plugins.
- Rejects write opens for NTFS metadata files below `FILE_first_user`.
- Marks file handles for close-time compressed, encrypted, and delayed mtime fixups.

`ntfs_fuse_read()`:

- Delegates reparse reads to plugins.
- Reads data with `ntfs_attr_pread()` in a loop.
- Caps reads to attribute size, with EFS raw size padding for encrypted nonresident attributes.
- Updates atime according to mount policy.

`ntfs_fuse_write()`:

- Delegates reparse writes to plugins.
- Writes in a loop with `ntfs_attr_pwrite()`.
- Updates mtime/ctime unless delayed mtime suppresses frequent updates.
- Sets the NTFS archive bit on successful writes.

`ntfs_fuse_release()`:

- Runs only when `fi->fh` carries deferred work.
- Delegates reparse release to plugins.
- Calls `ntfs_attr_pclose()` for compressed data.
- Calls `ntfs_efs_fixup_attribute()` for raw EFS-created/fixed streams.
- Applies delayed mtime updates.

## Truncation And Metadata Changes

- `ntfs_fuse_trunc()` backs both `truncate()` and `ftruncate()`.
- It rejects metadata files.
- Reparse truncation is plugin delegated.
- Compressed file upsizing writes a trailing zero to create a hole where possible; other cases use `ntfs_attr_truncate()`.
- Successful size changes set the archive bit and update mtime/ctime.
- `ntfs_fuse_chmod()` and `ntfs_fuse_chown()` require user mapping unless silent fallback is enabled; they update NTFS security descriptors and ctime.
- `ntfs_fuse_access()` is compiled when userspace permission checks are needed and checks parent search plus requested access.
- `ntfs_fuse_utimens()` or legacy `ntfs_fuse_utime()` implements timestamp setting with owner/write-access checks and NTFS timestamp conversion.
- macOS-specific handlers expose creation/change/backup time semantics, though backup time is only pretended because NTFS has no backup timestamp.

## Creation And Deletion

`ntfs_fuse_create()` is the shared object creation path for regular files, directories, symlinks, and device nodes:

- It validates file names, including optional Windows-name restrictions.
- It opens the parent directory and rejects creation under `$Extend`.
- It computes inherited or allocated NTFS security IDs when mappings are active.
- Reparse parent creation can be delegated to plugins.
- Normal creation calls `ntfs_create()`, `ntfs_create_symlink()`, or `ntfs_create_device()`.
- It applies security attributes if no reusable security ID was available.
- It sets archive state, marks close-time fixups on `fi`, and updates parent times.

Other creation/deletion helpers:

- `ntfs_fuse_create_stream()` adds a named `AT_DATA` attribute, creating the main file first if missing.
- `ntfs_fuse_mknod_common()` dispatches between normal object creation and named stream creation.
- `ntfs_fuse_symlink()` creates an Interix/NTFS symlink representation.
- `ntfs_fuse_link()` creates hard links, with parent-directory permission checks and plugin support for reparse parents.
- `ntfs_fuse_rm()` removes normal objects, rejects metadata files and `$Extend`, checks sticky-directory semantics, and uses `ntfs_delete()`.
- `ntfs_fuse_rm_stream()` removes a named `AT_DATA` stream.
- `ntfs_fuse_unlink()` dispatches between file removal and stream removal.
- `ntfs_fuse_mkdir()` and `ntfs_fuse_rmdir()` wrap create/remove for directories.

## Rename Semantics

`ntfs_fuse_rename()` implements rename through link/unlink operations:

- If the destination exists, it checks whether source and destination are the same inode.
- Existing destinations are handled by `ntfs_fuse_rename_existing_dest()`, which creates a temporary name using `.ntfs-3g-<sequence>`.
- `ntfs_fuse_safe_rename()` links the old destination to temp, unlinks destination, links source to destination, unlinks source, then cleans up temp or restores destination on failure.
- The source explicitly notes `FIXME: Rename should be atomic.`

This is a major behavioral difference from true POSIX atomic rename and is important for crash consistency, concurrent access, and applications depending on atomic replacement.

## Extended Attributes And Streams

All xattr support is under `HAVE_SETXATTR`.

Namespace handling:

- `xattr_namespace()` classifies names as `user.`, `system.`, `security.`, `trusted.`, open namespace, or none depending on stream mode.
- `fix_xattr_prefix()` strips `user.` for NTFS stream-backed user xattrs, prefixes protected namespaces with `ntfs-3g.`, or preserves names in open namespace mode.
- `ntfs_check_access_xattr()` centralizes access checks for internal NTFS system xattrs and POSIX ACL xattrs.

Operations:

- `ntfs_fuse_listxattr()` lists named data streams as xattrs and optional mapped system xattrs, after access checks and user-xattr eligibility checks.
- `ntfs_fuse_getxattr_windows()` exposes `ntfs.streams.list` when using Windows stream interface.
- `ntfs_fuse_getxattr()` first hijacks known NTFS system xattrs, then handles stream-backed user/open xattrs by opening named `AT_DATA` attributes.
- `ntfs_fuse_setxattr()` similarly routes system xattrs to security/xattr helpers or writes stream-backed xattr data, honoring create/replace flags and macOS resource fork behavior.
- `ntfs_fuse_removexattr()` forbids removal of core NTFS ACL/attribute/EFS/timestamp xattrs, routes removable system xattrs to helpers, and removes stream-backed xattrs with permission checks.

EFS raw mode affects xattr data sizes and can trigger EFS attribute fixups after writes.

## Reparse Plugin Integration

When plugins are enabled:

- Internal plugins are registered for mount points, symlinks, LX symlinks, WSL sockets/FIFOs/devices, and similar tags.
- `CALL_REPARSE_PLUGIN` selects a plugin for an inode and invokes the requested operation if available.
- Junction/symlink plugin handlers expose reparse points as POSIX symlinks, using `ntfs_make_symlink()`.
- WSL plugin handlers expose AF_UNIX, FIFO, char, and block reparse points as POSIX special file modes.
- Unsupported reparse points are commonly represented as symlinks pointing to a synthetic `unsupported reparse tag ...` string.

## Other FUSE Operations

- `ntfs_fuse_fsync()` syncs the whole NTFS device through `ntfs_device_sync()`.
- `ntfs_fuse_ioctl()` forwards requests to `ntfs_ioctl()`, rejecting compatibility ioctl mode.
- `ntfs_fuse_bmap()` maps file blocks to physical device blocks for nonresident, uncompressed, unencrypted unnamed data attributes.
- `ntfs_close()` logs permission cache stats, destroys security context, and unmounts the NTFS volume.
- `ntfs_fuse_destroy2()` calls `ntfs_close()` from FUSE teardown.

## Important Dependencies

This file depends on nearly the whole NTFS-3G stack:

- FUSE 2.6+ APIs and platform-specific FUSE extensions.
- libntfs volume mount/unmount/free-space APIs.
- inode, attribute, directory, index, runlist, time, security, xattr, EFS, object ID, EA, reparse, ioctl, and plugin layers.
- `ntfs-3g_common.c` for option parsing, plugin registry helpers, xattr listing, and shared context definitions.

## Notable Limitations And Risk Areas

- Rename is explicitly non-atomic and implemented with link/unlink/temp restoration.
- The global `ctx` and `ntfs_sequence` make concurrency assumptions important; the code itself notes possible concurrent directory-access failure during rename cleanup.
- Reparse support depends on internal handlers and dynamic plugins; missing plugin load is logged once and then unsupported tags degrade to synthetic symlinks or errors.
- Permission behavior changes substantially by compile-time `HPERMSCONFIG`, `POSIXACLS`, `HAVE_SETXATTR`, FUSE version, and platform macros.
- Named stream parsing through colon syntax conflicts with filenames containing `:` and is intentionally blocked in directory entries under Windows stream mode.
- EFS raw handling adjusts sizes and performs deferred fixups, so close paths matter for correctness.
- Metadata files and `$Extend` are guarded in many write paths, but each mutation path has to maintain those checks separately.
- xattr names are backed by NTFS named streams; namespace prefixing and mapped system xattrs can expose subtle compatibility behavior across Linux, macOS, and open namespace modes.
