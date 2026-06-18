# sources/user-network-fs/samba/source4/ntvfs/posix/pvfs_fsinfo.c

Purpose: answers filesystem information queries for PVFS shares, including space usage, volume labels, attributes, quotas, object IDs, and sector size.

Important APIs and functions: `pvfs_fsinfo` is the main dispatcher. `pvfs_blkid_fs_uuid` optionally obtains a filesystem UUID through libblkid. `pvfs_cache_base_fs_uuid` caches the base filesystem GUID in `pvfs->base_fs_uuid`.

Control flow: only space-related info levels call `sys_statvfs`; all levels stat the base directory for device/inode/time. DSKATTR scales block counts to fit legacy fields and caps old LANMAN clients at 2 GiB. Allocation/size/full-size levels return statvfs-derived counts with 512-byte sectors. Volume levels use base inode as serial and share name as label. Attribute info returns PVFS filesystem attributes and NTVFS fs type. Object ID zeroes fields, caches the UUID, and returns it. Sector-size info reports aligned 512-byte logical/physical sectors.

State and persistence: reads filesystem state via stat/statvfs and caches the base UUID in memory. No persistent writes occur.

Dependencies and integration points: used by NTVFS fsinfo dispatch. Depends on PVFS share state, libndr GUID parsing, optional libblkid, statvfs compatibility helpers, and protocol version.

Risks: reports fixed 512-byte sectors regardless of actual hardware; UUID lookup may silently return zero GUID; statvfs is skipped for levels that do not need it; LANMAN compatibility intentionally clips values. Test signals include every query level, stat/statvfs failure mapping, object ID with and without libblkid, LANMAN DSKATTR cap, share-name volume label, and invalid generic/unknown levels.
