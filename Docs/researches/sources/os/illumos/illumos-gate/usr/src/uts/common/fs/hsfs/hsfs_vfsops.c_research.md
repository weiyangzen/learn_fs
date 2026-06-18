# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/hsfs/hsfs_vfsops.c

## Role

Implements HSFS VFS operations, module initialization/finalization, mount option handling, volume descriptor discovery/parsing, root vnode setup, unmount, statvfs, vget, and root mounting.

## Module And Options

- Registers filesystem `hsfs` with VFS ops for mount, unmount, root, statvfs, vget, and mountroot.
- Defines mount options for global/noglobal, lowercase mapping, trailing dot, Rock Ridge, Joliet, Joliet long names, ISO9660:1999 `vers2`, read-only, and sector.
- `_init()`, `_fini()`, and `_info()` manage module lifecycle. `_fini()` frees vfs/vnode ops, mount lock, hsnode cache, and scheduler caches.
- `hsfsinit()` installs VFS ops, builds vnode ops, initializes `hs_mounttab_lock`, hsnode cache, and scheduler caches.

## Mount And Unmount

- `hsfs_mount()` enforces mount privilege, directory mountpoint, read-only mount, no unsupported remount, mountpoint busy checks, mount option flags, device lookup, tape rejection, and calls `hs_mountfs()`.
- `hsfs_unmount()` rejects forced unmount, requires root vnode count of one, calls `hs_synchash()`, removes mount table entry, closes/releases device vnode, frees path table data, kstats, scheduler queue, locks, and `hsfs`.
- `hsfs_root()` returns a held root vnode.
- `hsfs_statvfs()` reports read-only filesystem stats, fsid, base type, flags, name max, and volume id.
- `hsfs_vget()` finds an existing vnode by file id or reconstructs it via `hs_remakenode()`.

## Mount Core

- `hs_mountfs()` opens the block device read-only, rejects swap devices and zero-size devices, allocates `hsfs` and supplemental volume structs, discovers ISO or High Sierra volume descriptors, computes an fsid, links the mount into `hs_mounttab`, initializes VFS fields and locks, creates the root vnode, probes RRIP, chooses the active namespace, sets name limits/flags, initializes I/O scheduling and kstats, and marks the filesystem magic.
- Namespace selection prefers RRIP, ISO9660:1999, or Joliet according to discovered descriptors and explicit mount options. Explicit Joliet or `vers2` can force RRIP off; disabled options suppress their corresponding namespace.
- `hs_getrootvp()` creates the root vnode from the volume root record or remakes it if the root record is invalid.

## Volume Discovery And Parsing

- `hs_findhsvol()` scans up to 32 High Sierra volume descriptor sectors and parses the Standard File Structure descriptor.
- `hs_parsehsvol()` extracts volume size, logical block size, shifts, dates, path table info, volume set data, label, and root directory record; rejects zero or non-power-of-two block sizes.
- `hs_findisovol()` scans ISO descriptors for PVD, ISO9660:1999 SVD, and Joliet SVD, parses discovered volumes, then probes for an `MKI ` signature allowing extent LBNs as stable inode numbers.
- `hs_joliet_level()` recognizes Joliet levels from SVD escape sequences.
- `hs_parseisovol()` parses ISO volume metadata similarly to High Sierra parsing.
- `hs_copylabel()` copies volume labels, converting Joliet UCS-2 labels through `hs_joliet_cp()`.

## Device And Root Mount Helpers

- `hs_getmdev()` resolves the mount source, supports lofi-backed mounts through `vfs_get_lofi()`, checks block-device type, read access, mount conflicts, and major validity.
- `hsfs_mountroot()` mounts HSFS as root on `ROOT_INIT`, handles root device lookup, VFS locking/addition, root vnode assignment, and clock setting from volume dates.
- `hs_findvoldesc()` returns the starting volume descriptor sector, optionally using `CDROMREADOFFSET` for multisession media.

## Dependencies And Interactions

- Coordinates with `hsfs_node.c` for root/vnode creation and hash cleanup, `hsfs_subr.c` for dates/kstats/warnings, SUSP/RRIP probing for extension selection, and HSFS scheduler code for read scheduling.
