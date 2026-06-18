# File Research: sources/windows/winbtrfs/src/ubtrfs/ubtrfs.c

## Purpose

`ubtrfs.c` implements the user-mode WinBtrfs formatting DLL. It exposes FMIFS-style entry points used by Windows formatting tools, builds an initial single-device Btrfs filesystem image, writes root/chunk/extent/free-space metadata trees, writes superblocks, and asks the loaded kernel driver to probe the newly formatted volume.

The file also includes a stub `ChkdskEx`, configuration exports for sector/node size and feature flags, and support for multiple checksum algorithms.

## Local Formatting Model

The formatter builds a minimal in-memory representation rather than reusing the kernel driver's tree code:

- `btrfs_item`: one sorted key/data item.
- `used_space_extent`: tracks allocated regions inside a chunk.
- `btrfs_chunk`: chunk offset, `CHUNK_ITEM`, allocation cursor, used bytes, and used-space list.
- `btrfs_root`: one root tree, its eventual tree header/address/chunk, and sorted item list.
- `btrfs_dev`: one device item plus the next physical allocation offset.

Helper list functions implement the subset of Windows list behavior needed in user mode.

## Formatting Layout Construction

`write_btrfs` is the main filesystem creation routine. It creates roots for root, chunk, extent, device, checksum, filesystem, data relocation, and optional free-space/block-group trees. It initializes one device, detects SSD rotation status, allocates a system chunk and metadata/mixed chunk, inserts the device item, creates the default subvolume, initializes filesystem and relocation roots, assigns tree block addresses, adds block-group/free-space records, writes all roots, clears the first megabyte, and writes superblocks.

Chunk and device placement is handled by:

- `init_device`: initializes `DEV_ITEM`, UUIDs, IO alignment, and skips the first MiB for allocations.
- `add_chunk`: chooses system/metadata chunk sizes, DUP vs single-stripe layout, stripe length, and device extents.
- `find_chunk_offset`: allocates physical space for chunk stripes and adds `DEV_EXTENT` records.
- `superblock_collision` and `get_next_address`: avoid placing tree blocks in stripes overlapping well-known superblock mirror locations.

The formatter creates DUP system metadata on non-SSD devices, uses DUP metadata unless mixed groups are requested, and supports optional free-space cache and block-group tree feature flags.

## Tree and Metadata Writing

`assign_addresses` gives each root a tree block address in the system or metadata chunk, records used space, and creates either skinny metadata (`TYPE_METADATA_ITEM`) or full extent items (`TYPE_EXTENT_ITEM`) in the extent tree. It also inserts `ROOT_ITEM` records for non-root/chunk roots.

`write_roots` serializes every root as a single leaf tree block. It emits leaf node headers from sorted `btrfs_item` lists, packs item payloads from the end of the node, fills the tree header, computes the selected checksum, and writes the block through `write_data`.

`write_data` writes the same tree block to every stripe in the target chunk, which implements DUP-style mirroring for chunks with two stripes.

`write_superblocks` builds the `superblock`, computes bytes used from extent metadata, validates/converts the volume label to UTF-8, embeds the system chunk array, computes the selected checksum, and writes superblock copies at the standard `superblock_addrs` that fit on the device.

Checksum support covers CRC32C, XXHASH, SHA256, and BLAKE2 for both tree blocks and superblocks. `check_cpu` switches CRC32C to a hardware implementation on x86/x64 when SSE4.2 is available.

## Initial Filesystem Contents

The created filesystem includes a default subvolume layout:

- `set_default_subvol` creates the root-tree directory inode and a directory item named `default` pointing to `BTRFS_ROOT_FSTREE`.
- `init_fs_tree` creates the subvolume root inode and a `..` inode ref.
- `add_inode_ref` and `add_dir_item` build packed Btrfs inode-reference and directory-item records.
- `add_block_group_items` records block group usage either in the block group tree or extent tree.
- `populate_free_space_root` emits free-space extents and `FREE_SPACE_INFO` records for each chunk when the free-space cache compat-ro flag is enabled.

Timestamps are converted from Windows file time to Btrfs seconds/nanoseconds by `win_time_to_unix`.

## Format Entry Points

`FormatEx2` performs the actual format operation. It enables `SeManageVolumePrivilege`, selects hardware CRC support, validates checksum type, opens the target volume for read/write, queries length and geometry, derives sector and node sizes, sends initial progress, locks the volume, refuses to format one member of a mounted multi-device Btrfs filesystem, sends a whole-device TRIM request, sets required incompat flags, calls `write_btrfs`, dismounts/unlocks/closes the volume, and asks `\\Btrfs` to probe the volume with `IOCTL_BTRFS_PROBE_VOLUME` after success.

`FormatEx` adapts undocumented `format.exe`/FMIFS-style arguments (`DSTRING`, `STREAM_MESSAGE`, `options`) to `FormatEx2` and returns a Win32 `BOOL`.

Other exports:

- `SetSizes`: sets default sector and node size overrides.
- `SetIncompatFlags`: sets default Btrfs incompat feature flags.
- `SetCompatROFlags`: sets default compat-ro feature flags.
- `SetCsumType`: sets default checksum type.
- `GetFilesystemInformation`: stub returning true.
- `DllMain`: records the module handle on process attach.

`ChkdskEx` is also a stub; when given a callback it reports a one-line "stub, not implemented" output and returns success.

## Mounted Multi-Device Protection

`is_mounted_multi_device` reads and verifies the target superblock, extracts filesystem and device UUIDs, opens `\\Btrfs`, queries mounted filesystems with `IOCTL_BTRFS_QUERY_FILESYSTEMS`, and checks whether the target device belongs to a currently mounted multi-device filesystem. `FormatEx2` denies formatting in that case.

`look_for_device` walks variable-length `btrfs_filesystem_device` records to match the device UUID. `check_superblock_checksum` verifies the on-disk superblock checksum before trusting UUIDs.

## Dependencies and Cross-File Interactions

This file includes shared Btrfs format definitions from `../btrfs.h`, public IOCTL definitions from `../btrfsioctl.h`, CRC32C from `../crc32c.h`, and XXHASH from the bundled ZSTD library. It declares SHA256 and BLAKE2 helpers provided elsewhere in the WinBtrfs build.

At runtime it uses NT native file APIs (`NtReadFile`, `NtWriteFile`, `NtFsControlFile`, `NtDeviceIoControlFile`, `NtOpenFile`), Windows disk/storage IOCTLs, mountdev structures, ATA identify data for SSD detection, and Windows privilege APIs.

## Error Handling and Safety Notes

The formatter returns NTSTATUS failures for privilege, open, geometry, invalid parameter, label validation, allocation/IO, and mounted multi-device protections. Many internal allocations use `malloc` without exhaustive null checks in helper paths, so the code assumes formatter memory pressure is uncommon compared with kernel-mode paths.

The formatter only creates a single-device filesystem. Multi-device awareness is protective, not constructive. The entire tree model assumes each root fits in one leaf at format time.
