# File Research: sources/local-fs/apfs-fuse/apfsfuse/ApfsFuse.cpp

## Role

`ApfsFuse.cpp` is the main read-only FUSE frontend for `apfs-fuse`. It wires low-level FUSE callbacks to `ApfsLib` container, volume, directory, file, xattr, decompression, partition-map, and device abstractions.

## Global State And Configuration

- `ops` stores the low-level FUSE operation table.
- `g_disk_main` and `g_disk_tier2` hold primary and optional fusion-drive devices.
- `g_container` and `g_volume` hold the mounted APFS container and selected volume.
- `g_vol_id`, `g_xid`, and `g_snap_xid` select volume, checkpoint transaction, and snapshot.
- `g_uid`, `g_gid`, `g_set_uid`, and `g_set_gid` implement mount-time UID/GID override.
- `g_physblksize` controls sector size for partition parsing.
- `g_password` supplies an encrypted-volume passphrase.
- `FUSE_TIMEOUT` is set to one day for attribute and entry caching.

## FUSE Callback Behavior

- `apfs_getattr()` calls `apfs_stat_internal()` and replies with file attributes or `ENOENT`.
- `apfs_lookup()` resolves child names through `ApfsDir::LookupName()`, fills `fuse_entry_param`, and replies with entry metadata.
- `apfs_open()` rejects non-read-only opens, loads inode metadata, decompresses compressed files up front when needed, and stores a `File *` in `fi->fh`.
- `apfs_read()` reads uncompressed files through `ApfsDir::ReadFile()` using the inode private ID, or serves bytes from preloaded decompressed data.
- `apfs_opendir()` allocates a `Directory` handle.
- `apfs_readdir()` lazily builds a FUSE direntry buffer from `ApfsDir::ListDirectory()`.
- `apfs_readlink()` reads `com.apple.fs.symlink`.
- `apfs_getxattr()`/`apfs_getxattr_mac()` read named extended attributes; macOS also accepts a `position`.
- `apfs_listxattr()` lists attributes as NUL-separated names.
- `apfs_release()` and `apfs_releasedir()` delete per-handle state.
- `apfs_statfs()` reports block counts and free blocks from the APFS container.

## Metadata Mapping

`apfs_stat_internal()` maps APFS inode records into `struct stat`:

- Synthetic root parent inode `ROOT_DIR_PARENT` becomes inode 1, mode `0755`, directory, two links.
- APFS mode, owner, group, rdev, timestamps, and inode number are copied into platform-specific stat fields.
- UID/GID can be overridden globally from mount options.
- Regular file size is derived from uncompressed-size metadata, `com.apple.decmpfs`, resource fork size, data-stream size, or zero.
- Directory size is set from child/link count.

## Startup And Mount Flow

1. Initializes the FUSE operations table.
2. Sets default UID/GID from effective process credentials.
3. Parses command-line options: debug level, secondary fusion device, mount options, partition ID, volume ID, passphrase, container offset, and lax mode.
4. Requires exactly `<device> <dir>`.
5. Forces `ro` and sets `fsname` in FUSE mount options.
6. Parses `-o` options for `uid`, `gid`, `vol`, `blksize`, `pass`, `xid`, and `snap`.
7. Opens primary and optional secondary devices.
8. Applies physical block size override.
9. If no explicit offset is supplied, attempts GPT parsing to locate an APFS partition.
10. Constructs and initializes `ApfsContainer`.
11. Opens the selected APFS volume with passphrase and snapshot options.
12. Creates a FUSE 2 or FUSE 3 low-level session, daemonizes when debug is disabled, runs the session loop, unmounts, destroys the session, frees FUSE args, closes devices, and deletes APFS objects.

## Important Dependencies

- FUSE 2 or FUSE 3 low-level APIs.
- `ApfsLib/ApfsContainer`, `ApfsVolume`, `ApfsDir`, `Decmpfs`, `DeviceLinux`, `DeviceMac`, and `GptPartitionMap`.
- Platform stat timestamp fields differ for Linux and macOS.

## Notable Limitations And Risk Areas

- The filesystem is intentionally read-only; write opens return `EACCES` and no mutation callbacks are registered.
- Most state is process-global, which is simple for one mount but makes multi-mount-in-process use impractical.
- `apfs_lookup()` calls `fuse_reply_entry()` even if `apfs_stat_internal()` fails after name lookup; that can return partially initialized attributes.
- `apfs_read()` ignores the success/failure result of `ReadFile()` for uncompressed files and replies with a zero-filled buffer on failed or short reads.
- Compressed files are decompressed at open time into memory, which can be expensive for large files.
- `apfs_getxattr_mac()` replies with `min(data.size(), size)` from `data + position` without bounding `position` against `data.size()`.
- GPT partition selection reuses `partition_id` for the secondary device, so explicit primary partition state can affect secondary probing flow.
- Cleanup paths after some early errors do not always close/delete every object already opened, especially secondary-device paths.
