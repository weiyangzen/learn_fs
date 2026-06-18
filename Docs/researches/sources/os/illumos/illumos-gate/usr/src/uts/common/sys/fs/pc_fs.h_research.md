# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/pc_fs.h

This header defines PCFS/FAT mount state, boot-sector accessors, validation masks, FAT32 fsinfo, cluster constants, and filesystem helper interfaces.

Design notes:
- PCFS aims to remain mostly stateless except while files are open, allowing removable media changes.
- Disk changes are detected by comparing in-core directory entries with on-disk entries during directory searches.
- Files and directories use separate vnode op vectors and tables.
- FAT32 support introduces 32-bit clusters, non-fixed root directory location, fsinfo maintenance, optional alternate FAT behavior, and chunked FAT reads for large FATs.

Types:
- `pc_cluster16_t` and `pc_cluster32_t` define cluster-width types.
- Legacy `bootsec` and `fat32_bootsec` structs exist for compatibility, but active code uses byte-offset accessors.

Boot-sector access:
- Defines offsets for generic BPB, FAT12/16 extended BPB, and FAT32 extended BPB fields.
- `LE_16_NA` and `LE_32_NA` parse unaligned little-endian fields.
- `bpb_get_*` macros read sector size, sectors per cluster, reserved sectors, FAT count/size, media byte, geometry, hidden/total sectors, signatures, FAT32 root/fsinfo/backup fields, volume ids/labels, and filesystem type strings.

Validation:
- Macros validate sector size, sectors per cluster, cluster size, FAT count, reserved sectors, signatures, media descriptors, volume labels, OEM names, FAT type strings, jump boot instructions, FAT32 version, and extended flags.
- Individual `BPB_*_OK` bits record validation results.
- `FAT12_VALIDMSK`, `FAT16_VALIDMSK`, and `FAT32_VALIDMSK` define required structural checks; FAT32 deliberately does not require a boot signature to tolerate older SYSLINUX overwrites.
- Supported FAT32 FS version is 0.

FAT32 fsinfo:
- `fat_fsi_t` stores free cluster count and next-free search hint.
- `fat_od_fsi_t` models on-disk FAT32 FSI sector signatures and fields.
- `FSISIG_OK` validates lead/structure/trail signatures.
- `FSINFO_UNKNOWN` marks invalid free/next data.

Mount state:
- `struct pcfs` stores VFS, flags, drive, FAT type, device vnode/dev, sector/cluster geometry, FAT/root/data starts, cluster count, active node refs, next free cluster, in-core FAT, FAT changemap, invalidation/verify times, filesystem lock owner/count, fsinfo, mount list link, root vnode, timezone, media size/descriptor, last-cluster marker, root cluster, and root timestamp.
- Flags include FAT modified, locked/wanted, no check, boot partition, show hidden, PCMCIA pseudo floppy, fold case, fsinfo valid, irrecoverable write interference, no clamp time, and no atime.

Cluster and address macros:
- Define reserved/bad/last/free cluster constants for FAT12/16/32.
- Convert between offsets, logical blocks, clusters, disk blocks, and device block addresses.
- Check valid cluster range and directory entries per sector/cluster.

Mount args/options:
- Supports old and current mount arguments with timezone/DST/flags.
- Mount options include hidden/nohidden, foldcase/nofoldcase, clamptime/noclamptime, timezone, and secsize.

Kernel API:
- Lock/unlock filesystem, read/invalidate/sync FAT, count/allocate/set clusters, mark FAT updates, and query FAT-changed map.
- Debug print macros are gated by `pcfsdebuglevel`.

Dependencies and relationships:
- Works closely with `pc_dir.h`, `pc_node.h`, and `pc_label.h`.
- Stores FAT and filesystem layout state needed by vnode operations and directory lookup/update code.
