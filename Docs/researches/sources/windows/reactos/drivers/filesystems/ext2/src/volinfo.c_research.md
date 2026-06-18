# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/volinfo.c

This file implements Ext2 volume information query and set IRPs.

`Ext2QueryVolumeInformation` rejects the filesystem control device, validates the mounted VCB, acquires `MainResource` shared, zeroes the caller buffer, and handles `FileFsVolumeInformation`, `FileFsSizeInformation`, `FileFsDeviceInformation`, `FileFsAttributeInformation`, and Windows 2000+ `FileFsFullSizeInformation`.

Size information reports total/free allocation units from ext superblock counters, sectors per allocation unit from block size and disk geometry, and bytes per sector from disk geometry. Attribute information reports hard links, case sensitivity, preserved names, reparse points, extended attributes, read-only state, component name length, and filesystem name `EXT2`, `EXT3`, or `EXT4`.

`Ext2SetVolumeInformation` supports `FileFsLabelInformation`, rejects read-only volumes, limits labels to 16 WCHARs, copies the label to the VPB, converts it to OEM into `s_volume_name`, and saves the superblock.

Research note: `FileFsAttributeInformation` sets `FileSystemNameLength = 8` but copies `L"EXT4\0"`/`EXT3`/`EXT2` with 10 bytes, which appears to over-copy by one WCHAR relative to the advertised required length.
