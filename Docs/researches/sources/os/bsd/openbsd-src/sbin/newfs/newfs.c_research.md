# File Research: sources/os/bsd/openbsd-src/sbin/newfs/newfs.c

Purpose: Front-end for creating FFS filesystems and, when invoked as `mount_mfs`, memory filesystems. It parses CLI options, resolves devices/labels, enforces mounted-device safety, delegates layout creation to `mkfs()`, and optionally mounts MFS.

Mode selection:
- If program name contains `mfs`, sets MFS mode, dry-run-ish memory behavior, quiet mode, and FFS1 format.
- Non-MFS mode defaults to FFS2 when size is large enough unless overridden by `-O`.
- `-t` can dispatch to filesystem-specific tools such as `/sbin/newfs_<fstype>` or `/usr/sbin/newfs_<fstype>` when the type is not `ffs`.

Option handling:
- Parses block/fragment size, sectorsize, fragments-per-cylinder-group, max blocks per file per cylinder group, density, minfree, average file/directory estimates, optimization preference, explicit size, disk type, quiet, and dry-run.
- Uses `scan_scaled()` for sector and filesystem size options; suffix-bearing `-s` values are interpreted as bytes and rounded to sectors.

Device and label handling:
- Opens the output device read/write unless `-N`.
- Refuses to create over a currently mounted device by comparing raw/character device names against `getmntinfo()`.
- Reads disklabel with `DIOCGDINFO`, or falls back to named disktab type.
- Chooses partition from trailing device letter or numeric partition convention.
- Computes filesystem size from partition size or `-s`, then converts to DEV_BSIZE units for `mkfs()`.

Defaults:
- Fragment defaults come from disklabel fragblock or `max(2048, sector size)`.
- Block defaults come from disklabel fragblock or `min(16384, 8 * fsize)`.
- Density defaults to four fragments per inode, adjusted for large sector sizes.
- If `minfree` is below `MINFREE` and optimization was not explicitly chosen, optimization changes to space.

MFS behavior:
- Supports fake label for `mount_mfs swap`.
- Captures target mountpoint uid/gid/mode for root directory creation.
- After `mkfs()`, forks a child that mounts an anonymous `MOUNT_MFS` filesystem backed by `membase`.
- Optional `-P` pre-populates the MFS by temporarily mounting/copying via `/bin/pax`.

Support routines:
- `getphysmem()` reads `HW_PHYSMEM64` for later fsck memory warnings.
- `rewritelabel()` recomputes disklabel checksum and writes updated FFS partition metadata with `DIOCWDINFO`.
- `fatal()` logs to syslog if stderr is unavailable, useful for daemonized MFS child paths.
