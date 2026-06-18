# File Research: sources/os/bsd/netbsd-src/sys/sys/disk.h

Defines NetBSD disk device metadata, wedge interfaces, disk geometry, bad-sector reporting, strategy configuration, and kernel disk lifecycle APIs.

Key content:
- Disk info and geometry dictionary documentation.
- `struct dkwedge_info` and `struct dkwedge_list`.
- Common wedge partition type strings, including FFS, FAT, LFS, UDF, ZFS, CGD, RAIDframe, NTFS, ext2fs, VMFS, and aliases matching disklabel filesystem symbols.
- `struct disk_geom`.
- `struct disk_badsectors`, `struct disk_badsecinfo`.
- `struct disk_strategy` and `struct disk_sectoralign`.
- Kernel-only wedge discovery method registration macro.
- Extensive partition dictionary property schema documentation.
- `struct disk`: global link, name, info dictionary, geometry, open masks, state, block/byte shifts, I/O stats, driver, raw vnode state, wedge list, disklabel/cpulabel pointers.
- `struct dkdriver` operation vector.
- Disk states: closed/opening/read-label/open/raw.
- Disk and wedge lifecycle/query APIs.

Important behavior:
- Bridges disk drivers, disklabel handling, wedge autodiscovery, and user-visible disk metadata.
- Includes `dkio.h`, `time.h`, `queue.h`, and `iostat.h`.
