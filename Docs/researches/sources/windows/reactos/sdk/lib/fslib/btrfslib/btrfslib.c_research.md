# File Research: sources/windows/reactos/sdk/lib/fslib/btrfslib/btrfslib.c

Read completely: 1587 lines.

This is a Btrfs filesystem format library derived from WinBtrfs. It provides a ReactOS `BtrfsFormat` entry point and a non-ReactOS `FormatEx` entry point; checkdisk is a stub that only reports "stub, not implemented" and returns success. The format path opens and locks the target volume, determines size and geometry, chooses sector/node sizes, optionally trims the device, prevents formatting a mounted multi-device Btrfs member, writes a minimal Btrfs filesystem, dismounts/unlocks the volume, and asks the Btrfs driver to probe the volume.

Core in-memory builders create temporary roots, items, chunks, and a single device. `add_root`, `add_item`, `add_chunk`, `find_chunk_offset`, `assign_addresses`, `add_block_group_items`, `init_fs_tree`, and `set_default_subvol` construct root, chunk, extent, device, checksum, filesystem, and relocation trees. Items are sorted by Btrfs key order before serialization. `write_roots` serializes each root as a single leaf node, computes the selected checksum, and writes through chunk stripes with `write_data`.

Superblock and checksum paths support CRC32C, XXHash, SHA256, and BLAKE2 via `def_csum_type`. `write_superblocks` calculates filesystem bytes used, validates and encodes the label, fills `sys_chunk_array`, computes checksums, and writes superblocks at the standard Btrfs superblock offsets that fit on the device. ReactOS-specific code uses heap allocation wrappers, `RtlRandom`, and `RtlUnicodeStringToAnsiString`; non-ReactOS code adjusts privileges and may select hardware CRC32C on x86/x64.

Device safety checks include `is_ssd` using ATA identify data to decide whether to duplicate system/metadata chunks, `is_mounted_multi_device` reading an existing superblock and querying the loaded `\Btrfs` driver to avoid formatting one device from a mounted multi-device filesystem, and `do_full_trim` issuing a full-device TRIM request. `clear_first_megabyte` zeroes the first MiB before superblocks are written.

Public configuration helpers `SetSizes`, `SetIncompatFlags`, and `SetCsumType` set global defaults for later format calls. Defaults enable extended inode refs and skinny metadata; format also adds mixed backrefs and big metadata. `GetFilesystemInformation` and checkdisk are stubs.

Important interactions: uses Btrfs on-disk structures from driver headers, native NT file and device I/O (`NtOpenFile`, `NtWriteFile`, `NtReadFile`, `NtDeviceIoControlFile`, `NtFsControlFile`), FMIFS callbacks, mount manager structures, storage/TRIM IOCTLs, ATA identify IOCTLs, and Btrfs driver private IOCTLs.

Security/reliability notes: this code writes raw filesystem metadata and is data-destructive by design. It validates sector/node size relationships, checksum type, basic label characters/length, and some multi-device mount state. Several helper allocations are unchecked or assume success in non-error paths, cleanup is incomplete on some mid-format failures, global configuration is unsynchronized, UUID randomness is weak on ReactOS, and checkdisk is not implemented despite returning success. Formatting should be treated as trusted administrative code, not as robust handling of hostile inputs.
