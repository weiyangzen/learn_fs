# File Research: sources/local-fs/apfs-fuse/ApfsUtil/ApfsUtil.cpp

This file implements the `apfsutil` command-line utility. It opens an APFS device or image, optionally detects an APFS GPT partition, initializes an `ApfsContainer`, and prints basic volume information and snapshots.

The utility expects one argument: the device/image path. It sets `g_debug = 0`, opens the device through `Device::OpenDevice()`, defaults the APFS container byte range to the whole device, then attempts GPT detection through `GptPartitionMap`. If GPT validation succeeds, it lists partitions, finds the first APFS partition, and adjusts the offset/size passed to `ApfsContainer`.

After `container->Init()`, the program iterates up to `NX_MAX_FILE_SYSTEMS` and calls `GetVolumeInfo()` for each volume slot. For each present volume it prints volume index, UUID, role, name, case sensitivity derived from incompatible feature bits, consumed capacity in bytes, and a FileVault yes/no string based on APFS crypto flags.

If a volume has a snapshot metadata tree, the utility opens that B-tree at the volume superblock transaction ID, iterates entries from the beginning, filters for `APFS_TYPE_SNAP_METADATA`, and prints snapshot object IDs and names.

The helper `print_role()` maps APFS role bit flags and newer enum-shifted roles to human-readable labels. `print_filevault()` treats flags value `1` as not encrypted and everything else as encrypted.

Limitations: the utility is informational only and does not mount or repair. Partition names and volume names are printed directly with simple formatting. Snapshot iteration assumes the metadata tree is readable and stops when the key type no longer matches snapshot metadata.
