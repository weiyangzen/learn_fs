# File Research: sources/windows/reactos/drivers/filesystems/fs_rec/udfs.c

This file implements the UDF recognizer. It scans volume structure descriptors beginning at sector 16 and looks for UDF namespace identifiers.

`FsRecIsUdfsVolume` reads up to 16 sector-sized descriptors starting at `16 * SectorSize`. For each descriptor, it logs recognized identifiers and sets success if it sees either `NSR03` or `NSR02`. Other identifiers (`BEA01`, `TEA01`, `CD001`, `CDW02`, `BOOT2`) are logged but do not independently recognize UDF.

`FsRecUdfsFsControl` handles:
- `IRP_MN_MOUNT_VOLUME`: gets the sector size and calls `FsRecIsUdfsVolume`.
- `IRP_MN_LOAD_FILE_SYSTEM`: loads `\Registry\Machine\System\CurrentControlSet\Services\Udfs`.

Research notes:
- The file comment says `USFS Recognizer`, but implementation is UDFS/UDF.
- Recognition depends on the VSD sequence rather than anchor-volume descriptors.
- The loop stops on the first failed descriptor read and frees only the last allocated descriptor buffer.
