# File Research: sources/windows/reactos/drivers/filesystems/fs_rec/fat.c

FAT/VFAT recognizer. `FsRecIsFatVolume` unpacks the packed BPB with `FatUnpackBios`, normalizes the small-versus-large sector count, and validates the boot jump opcode, bytes per sector, sectors per cluster, nonzero reserved sectors, nonzero total sector count, accepted media byte values, and FAT12/16 root-entry consistency. It does not fully mount or classify FAT type; it only decides whether the boot sector is plausible enough to load FastFAT.

`FsRecVfatFsControl` handles mount by reading the first 512 bytes of the target device after retrieving sector size. A successful FAT signature check returns `STATUS_FS_DRIVER_REQUIRED`. Geometry/read failures set `DeviceError`, and floppy failures are treated permissively by requesting the filesystem driver anyway. Load requests call `FsRecLoadFileSystem` for the `fastfat` service.
